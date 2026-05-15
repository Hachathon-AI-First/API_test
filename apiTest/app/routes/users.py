from fastapi import APIRouter, HTTPException
from app.db import users_db
import asyncio

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users():
    # simulate async delay
    await asyncio.sleep(0.1)
    # returning list of dicts directly
    return users_db

@router.get("/{user_id}")
async def get_user(user_id: int):
    await asyncio.sleep(0.1)
    user = next((u for u in users_db if u["id"] == user_id), None)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/{user_id}")
async def update_user(user_id: int, user_data: dict):
    user = next((u for u in users_db if u["id"] == user_id), None)
    if user:
        user["username"] = user_data.get("username", user["username"])
        user["email"] = user_data.get("email", user["email"])
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.delete("/{user_id}")
async def delete_user(user_id: int):
    global users_db
    users_db = [u for u in users_db if u["id"] != user_id]
    return {"message": "User deleted"}
