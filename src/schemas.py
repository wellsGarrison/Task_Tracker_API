# import json
# from jsonschema import validate, ValidationError

user_registration = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["name", "email", "password"]
}

user_login = {
    "type": "object",
    "properties": {
        "email": {"type": "string"},
        "password": {"type": "string"}
    },
    "required": ["email", "password"]
}

create_task = {
    "type": "object",
    "properties": {
        "description": {"type": "string"}
        # "age": {"type": "number"},
        # "email": {"type": "string", "format": "email"}
    },
    "required": ["description"]
}

update_task = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "description": {"type": "string"}
    },
    "required": ["id", "description"]
}

delete_task = {
    "type": "object",
    "properties": {
        "id": {"type": "number"}
    },
    "required": ["id"]
}

mark_task = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "status": {"type": "string"}
    },
    "required": ["id", "status"]
}

list_task = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "page": {"type": "number"},
        "limit": {"type": "number"}
    },
    "required": ["page", "limit"]
}