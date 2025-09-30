import datetime
from enum import Enum
# import api

class Status(Enum):
    TODO = 1
    INPROGRESS = 2
    DONE = 3

print(type(Status.TODO))

class Task:
    def __init__(self, id, desription, status: Status, createdAt, updatedAt) -> None:
        self.id = id
        self.description = desription
        self.status = status
        self.createdAt = createdAt
        self.updatedAt = updatedAt



    
