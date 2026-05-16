from fastapi import APIRouter, Query
from typing import Optional
from app.db import orders_db, products_db, users_db, payments_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/revenue/daily")
def get_daily_revenue(date: str = Query(..., description="Date in YYYY-MM-DD format")):
    """Returns total revenue for a given day."""
    total = sum(p["amount"] for p in payments_db if p["status"] == "success")
    return {"date": date, "revenue": total}

@router.get("/revenue/monthly")
def get_monthly_revenue(year: int, month: int):
    """Returns total revenue for a given month."""
    total = sum(p["amount"] for p in payments_db if p["status"] == "success")
    return {"year": year, "month": month, "revenue": total}

@router.get("/products/top-selling")
def get_top_selling_products(limit: int = Query(10, ge=1, le=100)):
    """Returns the top N selling products by units sold."""
    sales: dict[int, int] = {}
    for order in orders_db:
        for item in order.get("items", []):
            pid = item["product_id"]
            sales[pid] = sales.get(pid, 0) + item["quantity"]

    sorted_products = sorted(sales.items(), key=lambda x: x[1], reverse=True)[:limit]
    result = []
    for pid, qty in sorted_products:
        product = next((p for p in products_db if p["id"] == pid), None)
        if product:
            result.append({"product": product, "units_sold": qty})
    return result

@router.get("/users/activity")
def get_user_activity(user_id: Optional[int] = None):
    """Returns order count and total spend per user."""
    stats: dict[int, dict] = {}
    for order in orders_db:
        uid = order["user_id"]
        if user_id and uid != user_id:
            continue
        if uid not in stats:
            stats[uid] = {"order_count": 0, "total_spent": 0.0}
        stats[uid]["order_count"] += 1
        stats[uid]["total_spent"] += order["total_price"]
    return stats

@router.get("/orders/status-breakdown")
def get_order_status_breakdown():
    """Returns count of orders grouped by status."""
    breakdown: dict[str, int] = {}
    for order in orders_db:
        status = order["status"]
        breakdown[status] = breakdown.get(status, 0) + 1
    return breakdown

@router.get("/products/low-stock")
def get_low_stock_alert(threshold: int = Query(5, ge=0)):
    """Returns products with stock below the given threshold."""
    return [p for p in products_db if p["stock"] <= threshold]

@router.get("/payments/method-breakdown")
def get_payment_method_breakdown():
    """Returns revenue grouped by payment method."""
    breakdown: dict[str, float] = {}
    for payment in payments_db:
        if payment["status"] == "success":
            method = payment["method"]
            breakdown[method] = breakdown.get(method, 0.0) + payment["amount"]
    return breakdown
