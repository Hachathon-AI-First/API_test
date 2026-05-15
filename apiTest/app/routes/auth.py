from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db import users_db

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest):
    # missing proper type hints for return
    user = next((u for u in users_db if u["username"] == request.username and u["password"] == request.password), None)
    if user:
        return {"access_token": "fake-jwt-token-123", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/register")
def register(user_data: dict):
    # Takes raw dict instead of Pydantic model
    new_id = len(users_db) + 1
    new_user = {
        "id": new_id,
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "password": user_data.get("password")
    }
    users_db.append(new_user)
    return {"message": "User registered successfully", "user_id": new_id}

@router.post("/refresh-token")
def refresh_token(token: str):
    if token == "fake-jwt-token-123":
         return {"access_token": "new-fake-jwt-token-456", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid token")
