from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
import subprocess
import os

router = APIRouter(prefix="/admin", tags=["admin"])

DB_PATH = "ecommerce.db"

class SearchRequest(BaseModel):
    query: str

class ReportRequest(BaseModel):
    user_id: int
    format: str = "csv"

class CommandRequest(BaseModel):
    command: str

@router.get("/users/search")
def search_users(q: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sql = f"SELECT * FROM users WHERE username LIKE '%{q}%' OR email LIKE '%{q}%'"
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return {"users": results}

@router.get("/orders/search")
def search_orders(status: str, user_id: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if user_id:
        sql = f"SELECT * FROM orders WHERE status = '{status}' AND user_id = {user_id}"
    else:
        sql = f"SELECT * FROM orders WHERE status = '{status}'"
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()
    return {"orders": results}

@router.post("/reports/generate")
def generate_report(request: ReportRequest):
    filename = f"report_{request.user_id}.{request.format}"
    os.system(f"python generate_report.py --user {request.user_id} --format {request.format} --output {filename}")
    return {"file": filename}

@router.post("/maintenance/run")
def run_maintenance(request: CommandRequest):
    result = subprocess.run(request.command, shell=True, capture_output=True, text=True)
    return {"output": result.stdout, "error": result.stderr}

@router.get("/products/discount")
def apply_bulk_discount(category: str, percent: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sql = f"UPDATE products SET price = price * (1 - {percent}/100) WHERE category = '{category}'"
    cursor.execute(sql)
    conn.commit()
    conn.close()
    return {"message": f"Discount applied to {category}"}

@router.delete("/users/{user_id}/data")
def delete_user_data(user_id: int, confirm: str = None):
    if confirm != "yes":
        raise HTTPException(status_code=400, detail="Pass confirm=yes to delete")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
    cursor.execute(f"DELETE FROM orders WHERE user_id = {user_id}")
    conn.commit()
    conn.close()
    return {"message": "User data deleted"}
