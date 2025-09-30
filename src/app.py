from flask import Flask, request, jsonify
from database.Data import DataHandler
from schemas import *
# from pymongo import MongoClient
import psycopg2
from jsonschema import validate, ValidationError


app = Flask(__name__)
dh = None

# validate json, pass json to DataHandler to add task to db
@app.route("/addTask", methods=["POST"])
def addTask():
    data = request.get_json()

    # validate json 
    try:
        validate(instance=data, schema=create_task_schema)
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
    # TODO: validate input
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
    app.run(port= 5000, debug=True)
    dh.close()
    