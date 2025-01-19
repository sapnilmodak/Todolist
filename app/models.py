from pydantic import BaseModel

class User(BaseModel):
    email: str
    password: str

class ToDoItem(BaseModel):
    id: int | None = None
    title: str
    completed: bool = False
