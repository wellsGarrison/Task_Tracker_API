# import json
# from jsonschema import validate, ValidationError

create_task_schema = {
    "type": "object",
    "properties": {
        "description": {"type": "string"}
        # "age": {"type": "number"},
        # "email": {"type": "string", "format": "email"}
    },
    "required": ["description"]
}

update_task_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "description": {"type": "string"}
    },
    "required": ["id", "description"]
}

delete_task_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"}
    },
    "required": ["id"]
}

mark_task_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "status": {"type": "string"}
    },
    "required": ["id", "status"]
}

list_task_schema = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "page": {"type": "number"},
        "limit": {"type": "number"}
    },
    "required": ["page", "limit"]
}