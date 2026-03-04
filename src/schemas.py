# JSON schemas for validating provided data. 

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
        "title": {"type": "string"},
        "description": {"type": "string"}
    },
    "required": ["title", "description"]
}

update_task = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "status": {"type": "string"}
    }
}
