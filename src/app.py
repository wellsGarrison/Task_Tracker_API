from flask import Flask, request, jsonify
from database.Data import DataHandler
# from schemas import *
import schemas
# from pymongo import MongoClient
import psycopg2
from jsonschema import validate, ValidationError
from argon2 import PasswordHasher
import datetime


app = Flask(__name__)
dh = None
ph = None

@app.route("/createAccount", methods=["POST"])
def createAccount():
    data = request.get_json()
    
    try:
        validate(instance=data, schema=schemas.user_registration)
        print("Valid data conforms to the schema.")
    except ValidationError as e:
        print(f"Validation Error for valid_data: {e.message}")
        return jsonify(data), 400
    
    # TODO
    # generate salt, concat with password, then hash
    hash = ph.hash(data['password'])
    user_id = None # make this a NanoID

    # generate token 
    jwt_payload = {
        "sub": user_id,
        "exp": datetime.datetime.now() + 5
    }

    # pass to DataHandler
    dh.createAccount(data['name'], data['email'], hash)
    # return token if user registered, return error otherwise 


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    try:
        validate(instance=data, schema=schemas.user_login)
        print("Valid data conforms to the schema.")
    except ValidationError as e:
        print(f"Validation Error for valid_data: {e.message}")
        return jsonify(data), 400
    
    # TODO 
    # get salt and hash and compare with password 
    # return token or error 


# validate json, pass json to DataHandler to add task to db
@app.route("/addTask", methods=["POST"])
def addTask():
    data = request.get_json()

    # TODO
    # check authentication token 

    # validate json 
    try:
        validate(instance=data, schema=schemas.create_task)
        print("Valid data conforms to the schema.")
    except ValidationError as e:
        print(f"Validation Error for valid_data: {e.message}")
        return jsonify(data), 400

    description = data['description']
    dh.addTask(description)

    return data, 201

# @app.route("/deleteTask/<taskId>", methods=["DELETE"])
# def deleteTask(taskId):
#     ret = dh.deleteTask(taskId)

# /todos?page=1&limit=10
@app.route("/list/", methods=['GET'])
def getTasks():
    # TODO: 
    # validate input
    # check auth token 

    page = request.args.get('page')
    limit = request.args.get('limit')
    status = request.args.get('status')

    lst = dh.getTasks(status, int(page), int(limit))

    return jsonify(lst), 200





if __name__ == "__main__":
    # client = MongoClient()
    # client.admin.command('ping')
    # print("Successfully connected to MongoDB!")
    dh = DataHandler()
    ph = PasswordHasher()
    app.run(port= 5000, debug=True)
    dh.close()
    