from fastapi import FastAPI, HTTPException, Depends
from app.database import get_table
from app.auth import hash_password, verify_password, create_access_token, get_current_user
from app.models import User, ToDoItem
from datetime import timedelta

app = FastAPI()

# Constants
USERS_TABLE = "users"
TODOS_TABLE = "todos"

@app.post("/register/")
def register(user: User):
    users_table = get_table(USERS_TABLE)
    # Check if the user exists
    existing_user = users_table.select("*").eq("email", user.email).execute()
    if existing_user.data:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password and save user
    hashed_password = hash_password(user.password)
    users_table.insert({"email": user.email, "password": hashed_password}).execute()
    return {"message": "User registered successfully"}

@app.post("/token/")
def login(user: User):
    users_table = get_table(USERS_TABLE)
    # Find user
    db_user = users_table.select("*").eq("email", user.email).execute()
    if not db_user.data or not verify_password(user.password, db_user.data[0]["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate JWT token
    access_token = create_access_token(data={"sub": db_user.data[0]["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/todos/", response_model=ToDoItem)
def create_todo(todo: ToDoItem, current_user: str = Depends(get_current_user)):
    todos_table = get_table(TODOS_TABLE)
    result = todos_table.insert({"user_id": current_user, "title": todo.title, "completed": todo.completed}).execute()
    todo.id = result.data[0]["id"]
    return todo

@app.get("/todos/", response_model=list[ToDoItem])
def get_todos(current_user: str = Depends(get_current_user)):
    todos_table = get_table(TODOS_TABLE)
    result = todos_table.select("*").eq("user_id", current_user).execute()
    return result.data

@app.put("/todos/{todo_id}/", response_model=ToDoItem)
def update_todo(todo_id: int, todo: ToDoItem, current_user: str = Depends(get_current_user)):
    todos_table = get_table(TODOS_TABLE)
    result = todos_table.update({"title": todo.title, "completed": todo.completed}).eq("id", todo_id).eq("user_id", current_user).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Todo not found")
    return result.data[0]

@app.delete("/todos/{todo_id}/")
def delete_todo(todo_id: int, current_user: str = Depends(get_current_user)):
    todos_table = get_table(TODOS_TABLE)
    result = todos_table.delete().eq("id", todo_id).eq("user_id", current_user).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"message": "Todo deleted successfully"}
