from flask import Flask, request, jsonify, g
from database.Data import DataHandler
# from schemas import *
import schemas
# from pymongo import MongoClient
import psycopg2
from jsonschema import validate, ValidationError
from argon2 import PasswordHasher
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import jwt
from uuid import uuid7
from jwt.exceptions import ExpiredSignatureError
from functools import wraps
from argon2.exceptions import VerifyMismatchError
import config
from Task.Task import Task, Status


app = Flask(__name__)
dh = None
ph = None
load_dotenv()

def token_required(f):
    @wraps(f)
    def check_token(*args, **kwargs):
        auth = request.authorization
        if auth and auth.type == 'bearer':
            token = auth.token
            # Validate token logic...
            try:
                claim = jwt.decode(token, key=os.getenv('JWT_secret'), algorithms=['HS256', ])
                g.user_id = claim['sub']
            except ExpiredSignatureError as e:
                return jsonify({"message": "Unauthorized: expired token"}), 401
            except Exception as e:
                return jsonify({"message": "Unauthorized: invalid token"}), 401
        else:
            return jsonify({"message": "Unauthorized"}), 401
        
        return f(*args, **kwargs)
        
    return check_token

@app.route("/create_account", methods=["POST"])
def create_account():
    data = request.get_json()
    
    try:
        validate(instance=data, schema=schemas.user_registration)
        # print("Valid data conforms to the schema.")
    except ValidationError as e:
        print(f"Validation Error for valid_data: {e.message}")
        return jsonify(data), 400
    
    # hash password and generate user_id
    hash = ph.hash(data['password'])
    user_id = str(uuid7())

    # generate token 
    # exp = datetime.now(tz=timezone.utc).timestamp() + 60*5
    jwt_payload = {
        "sub": user_id,
        "exp": datetime.now(tz=timezone.utc).timestamp() + config.token_timeout
    }
    secret = os.getenv('JWT_secret')
    token = jwt.encode(
        payload=jwt_payload,
        key=secret
    )

    # pass to DataHandler
    try:
        dh.create_account(data['name'], data['email'], hash, user_id)
    except psycopg2.DatabaseError as e:
        if str(e).startswith('duplicate key value violates unique constraint "unique_email"'):
            return jsonify({"message": "email already in use"}), 409
        # print(e.args[0])
        else:
            print(e)
            return jsonify({"message": "database error"}), 500

    # return token if user registered, return error otherwise 
    return jsonify({"token": token}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    try:
        validate(instance=data, schema=schemas.user_login)
        # print("Valid data conforms to the schema.")
    except ValidationError as e:
        print(f"Validation Error for data: {e.message}")
        return jsonify(data), 400
    
    # TODO 
    # get salt and hash and compare with password 
    # print(data['email'])
    email = data['email']
    password = data['password']
    try:
        hash = dh.get_hash(email)
        if not hash:
            return jsonify({'message': 'email not found'}), 401
    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return jsonify({'message': 'database error'}), 500

    try:
        ph.verify(hash, password)
    except VerifyMismatchError as e:
        return jsonify({'message': 'incorrect password'}), 401
    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return jsonify({'message': 'incorrect password'}), 401
    
    # return token or error 
    # generate token 
    try:
        user_id = dh.get_user_id(email)
        if ph.check_needs_rehash(hash):
            dh.set_password_hash_for_user(user_id, ph.hash(password))
        if not user_id:
            return jsonify({'message': 'email not found'}), 401
    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return jsonify({'message': 'database error'}), 401
    
    jwt_payload = {
        "sub": user_id,
        "exp": datetime.now(tz=timezone.utc).timestamp() + config.token_timeout
    }
    secret = os.getenv('JWT_secret')
    token = jwt.encode(
        payload=jwt_payload,
        key=secret
    )

    # return token if user registered, return error otherwise 
    return jsonify({"token": token}), 201


# validate json, pass json to DataHandler to add task to db
@app.route("/todos", methods=["POST"])
@token_required
def add_task():
    data = request.get_json()
    user_id = g.user_id
    # TODO
    # check authentication token     
    
    # validate json 
    try:
        validate(instance=data, schema=schemas.create_task)
        # print("Valid data conforms to the schema.")
    except ValidationError as e:
        print(f"Validation Error for valid_data: {e.message}")
        return jsonify(data), 400
    


    # description = data['description']
    task_id = str(uuid7())
    title  = data['title']
    desc = data['description']
    dh.add_task(user_id, task_id, title, desc)

    return jsonify({
        'id': task_id,
        'title': title,
        'description': desc
    }), 201

@app.route("/todos/<task_id>", methods=["PUT"])
@token_required
def update_task(task_id):
    data = request.get_json()
    user_id = g.user_id

    try:
        validate(instance=data, schema=schemas.update_task)
        # print("Valid data conforms to the schema.")
    except ValidationError as e:
        print(f"Validation Error for update_task: {e.message}")
        return jsonify(data), 400
    
    # task_id = data['task_id']
    rtn = None
    try:
        if "status" in data.keys():
            if data['status'] in Status._member_names_:
                rtn = dh.change_status(user_id, task_id, data['status'])
            else:
                return 'invalid status', 400
            
        elif "title" in data.keys() and "description" in data.keys():
            rtn = dh.change_task(user_id, task_id, data['title'], data['description'])

    except psycopg2.DatabaseError as e:
        print(e)
        return jsonify({"message": "database error"}), 500
    
    if rtn == 0:
        return jsonify({"message": "task not found in user's tasks"}), 404
    else:
        data['task_id'] = task_id
        return jsonify(data), 204 
    

# @app.route("/mark_task", methods=["PUT"])
# def mark_task():
#     data = request.get_json()  


@app.route("/todos/<task_id>", methods=["DELETE"])
@token_required
def delete_task(task_id):
    # data = request.get_json()
    user_id = g.user_id

    # try:
    #     validate(instance=data, schema=schemas.delete_task)
    #     # print("Valid data conforms to the schema.")
    # except ValidationError as e:
    #     print(f"Validation Error for valid_data: {e.message}")
    #     return jsonify(data), 400

    rtn = dh.delete_task(user_id, task_id)
    if rtn == 0:
        return jsonify({"message": "task not found in user's tasks"}), 404
    else:
        # data['task_id'] = task_id
        return '', 204 

# /todos?page=1&limit=10
@app.route("/todos", methods=['GET'])
@token_required
def get_tasks():
    # TODO: 
    # validate input
    # check auth token 
    user_id = g.user_id

    page = request.args.get('page', default=1)
    limit = request.args.get('limit', default=10)
    status = request.args.get('status', default=None)
    print(status)

    lst = dh.get_tasks(user_id, status, int(page), int(limit))

    return jsonify(lst), 200





if __name__ == "__main__":
    # client = MongoClient()
    # client.admin.command('ping')
    # print("Successfully connected to MongoDB!")
    dh = DataHandler()
    ph = PasswordHasher()
    app.run(port= 5000, debug=True)
    dh.close()
    