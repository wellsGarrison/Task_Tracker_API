from flask import Flask, request, jsonify, g
from database.Data import DataHandler
import schemas
import psycopg2
from jsonschema import validate, ValidationError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import jwt
from uuid import uuid7
from jwt.exceptions import ExpiredSignatureError
from functools import wraps
import config
from Task.Task import Status


app = Flask(__name__)
dh = None
ph = None
load_dotenv()

# Wrapper for validating session tokens 
def token_required(f):
    @wraps(f)
    def check_token(*args, **kwargs):
        # Authentication done with JWT stored in the authorization header
        auth = request.authorization
        if auth and auth.type == 'bearer':
            token = auth.token
            try:
                # use PyJWT to decode token, token includes user_id and expiration timestamp
                # store user_id in the flask.g object so it can be accessed in other methods 
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

# User registration route, return authentication token if registered succesfully, error otherwise 
@app.route("/create_account", methods=["POST"])
def create_account():
    data = request.get_json()
    
    # Validate JSON
    try:
        validate(instance=data, schema=schemas.user_registration)
    except ValidationError as e:
        print(f"Validation Error for user_registration: {e.message}")
        return jsonify(data), 400
    
    # hash password and generate user_id
    hash = ph.hash(data['password'])
    user_id = str(uuid7())

    # generate token, token_timeout measured in seconds
    jwt_payload = {
        "sub": user_id,
        "exp": datetime.now(tz=timezone.utc).timestamp() + config.token_timeout
    }
    # encode using HS256
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
        else:
            print(e)
            return jsonify({"message": "database error"}), 500

    # return token if user registered, return error otherwise 
    return jsonify({"token": token}), 201

# Login route, return authentication token if crednetials are valid, error otherwise 
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    # Validate JSON
    try:
        validate(instance=data, schema=schemas.user_login)
    except ValidationError as e:
        print(f"Validation Error for user_login: {e.message}")
        return jsonify(data), 400
    
    # get salt and hash (Argon2 hash contains hash and salt)
    email = data['email']
    password = data['password']
    try:
        hash = dh.get_hash(email)
        if not hash:
            return jsonify({'message': 'email not found'}), 401
    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return jsonify({'message': 'database error'}), 500

    # Validate password against hash
    try:
        ph.verify(hash, password)
    except VerifyMismatchError as e:
        return jsonify({'message': 'incorrect password'}), 401
    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return jsonify({'message': 'incorrect password'}), 401
    
    # Get user_id and regenerate hash if necessary 
    try:
        user_id = dh.get_user_id(email)
        if ph.check_needs_rehash(hash):
            dh.set_password_hash_for_user(user_id, ph.hash(password))
        if not user_id:
            return jsonify({'message': 'email not found'}), 401
    except Exception as e:
        print(f"Unexpected {e=}, {type(e)=}")
        return jsonify({'message': 'database error'}), 401
    
    # generate token, token_timeout measured in seconds
    jwt_payload = {
        "sub": user_id,
        "exp": datetime.now(tz=timezone.utc).timestamp() + config.token_timeout
    }
    # encode using HS256
    secret = os.getenv('JWT_secret')
    token = jwt.encode(
        payload=jwt_payload,
        key=secret
    )

    # return token 
    return jsonify({"token": token}), 201


# Add task route. validate json, pass json to DataHandler to add task to db
# Return task details with a task_id and status code 201 on success 
@app.route("/todos", methods=["POST"])
@token_required
def add_task():
    data = request.get_json()
    user_id = g.user_id   
    
    # validate json 
    try:
        validate(instance=data, schema=schemas.create_task)
    except ValidationError as e:
        print(f"Validation Error for create_task: {e.message}")
        return jsonify(data), 400
    
    # generate task_id, pass task details to data handler 
    task_id = str(uuid7())
    title  = data['title']
    desc = data['description']
    dh.add_task(user_id, task_id, title, desc)

    # return task details and status code 
    return jsonify({
        'id': task_id,
        'title': title,
        'description': desc
    }), 201

# Update task route. Change the status of a task or edit the title and description. 
# return task details with task_id on success 
@app.route("/todos/<task_id>", methods=["PUT"])
@token_required
def update_task(task_id):
    data = request.get_json()
    user_id = g.user_id

    # validate JSON
    try:
        validate(instance=data, schema=schemas.update_task)
    except ValidationError as e:
        print(f"Validation Error for update_task: {e.message}")
        return jsonify(data), 400
    
    # change status or title and description depending on what was provided 
    # rtn will be 1 if a task with the given task_id is found, 0 if not
    # obfuscates if user doesn't have access to task or if the task doesn't exist 
    rtn = 0
    try:
        if "status" in data.keys():
            # validate status is TODO, INPROGRESS, or DONE
            if data['status'] in Status._member_names_:
                # pass to data handler 
                rtn = dh.change_status(user_id, task_id, data['status'])
            else:
                return 'invalid status', 400
            
        elif "title" in data.keys() and "description" in data.keys():
            # pass to data handler 
            rtn = dh.change_task(user_id, task_id, data['title'], data['description'])

    except psycopg2.DatabaseError as e:
        print(e)
        return jsonify({"message": "database error"}), 500
    
    if rtn == 0:
        return jsonify({"message": "task not found in user's tasks"}), 404
    else:
        data['task_id'] = task_id
        return jsonify(data), 204 

# Delete task route, return 204 on successful delete, error otherwise 
@app.route("/todos/<task_id>", methods=["DELETE"])
@token_required
def delete_task(task_id):
    user_id = g.user_id

    # pass to data handler 
    # rtn will be 1 if a task with the given task_id is found, 0 if not
    # obfuscates if user doesn't have access to task or if the task doesn't exist 
    rtn = dh.delete_task(user_id, task_id)
    if rtn == 0:
        return jsonify({"message": "task not found in user's tasks"}), 404
    else:
        return '', 204 

# List tasks route, arguments for page, limit, and to filter by status. 
# returns a dictionary with a list of tasks, the page, limit, and total returned 
@app.route("/todos", methods=['GET'])
@token_required
def get_tasks():
    user_id = g.user_id

    page = request.args.get('page', default=1)
    limit = request.args.get('limit', default=10)
    status = request.args.get('status', default=None)

    lst = dh.get_tasks(user_id, status, int(page), int(limit))

    return jsonify(lst), 200





if __name__ == "__main__":
    dh = DataHandler()
    ph = PasswordHasher()
    app.run(port= 5000, debug=True)
    dh.close()
    