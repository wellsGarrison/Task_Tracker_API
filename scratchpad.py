import json
from jsonschema import validate, ValidationError

create_task_schema = {
    "type": "object",
    "properties": {
        "description": {"type": "string"},
        "age": {"type": "number"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "age"]
}



update_task_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "description": {"type": "string"}
    },
    "required": ["id", "name"]
}

# Valid JSON data
valid_data = {"name": "Charlie", "age": 40, "email": "charlie@example.com"}

# Invalid JSON data (missing required field)
invalid_data_1 = {"name": "David", "email": "david@example.com"}

# Invalid JSON data (incorrect data type)
invalid_data_2 = {"name": "Eve", "age": "fifty"}

try:
    validate(instance=valid_data, schema=schema)
    print("Valid data conforms to the schema.")
except ValidationError as e:
    print(f"Validation Error for valid_data: {e.message}")