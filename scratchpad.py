import json
from jsonschema import validate, ValidationError
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import jwt
import psycopg2
import uuid


# print(os.getenv('JWT_secret'))

# conn = psycopg2.connect(
#                 dbname="task_tracker_db",
#                 user="postgres",
#                 password="",
#                 host="localhost",
#                 port="5432"
#             )
# cur = conn.cursor()

# cur.execute("""
#             UPDATE tasks
#             SET status = 'DONE'
#             WHERE title='a'
#             """)
# conn.commit()
# # temp = cur.fetchall()
# print(cur.rowcount)


# user_id = "1"
# jwt_payload = {
#     "sub": user_id,
#     "exp": datetime.now(tz=timezone.utc).timestamp() + 60*5
# }
# secret = 'surprise-sulk-remarry-buccaneer-improper-}-@'
# token = jwt.encode(
#     payload=jwt_payload,
#     key=secret
# )
# print(token)


schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"},
        "email": {"type": "string"}
    },
    "required": ["name", "age"]
}

# Valid JSON data
# valid_data = {"name": "Charlie", "age": 40, "email": "charlie@example.com"}

# # Invalid JSON data (missing required field)
# invalid_data_1 = {"name": "David", "email": "david@example.com"}

# # Invalid JSON data (incorrect data type)
# invalid_data_2 = {"name": "Eve", "age": "fifty"}

# # validate(instance=invalid_data_1, schema=schema)

# try:
#     validate(instance=invalid_data_1, schema=schema)
#     print("Valid data conforms to the schema.")
# except ValidationError as e:
#     print(f"Validation Error for valid_data: {e.message}")