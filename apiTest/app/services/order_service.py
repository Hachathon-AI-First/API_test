from app.db import orders_db, products_db
from app.utils.helpers import calculate_discount

def create_order_in_db(user_id, items, coupon_code=None, shipping_address=None, priority=False):
    total = 0
    for item in items:
        product = next((p for p in products_db if p["id"] == item.product_id), None)
        if product:
            if product["stock"] >= item.quantity:
                total += product["price"] * item.quantity
                product["stock"] -= item.quantity
            else:
                return {"error": f"Not enough stock for product {item.product_id}"}
        else:
            return {"error": f"Product {item.product_id} not found"}

    if total > 1000:
        disc = total * (10/100)
        total = total - disc

    if coupon_code == "DISCOUNT20":
        total = total * 0.80

    order_id = len(orders_db) + 1
    new_order = {
        "id": order_id,
        "user_id": user_id,
        "items": [{"product_id": i.product_id, "quantity": i.quantity} for i in items],
        "total_price": total,
        "status": "created",
        "priority": priority,
        "shipping_address": shipping_address,
    }
    orders_db.append(new_order)
    return new_order

def get_orders_by_user(user_id, status_filter=None, limit=50):
    user_orders = []
    for order in orders_db:
        if order["user_id"] == user_id:
            if status_filter is None or order["status"] == status_filter:
                user_orders.append(order)
    return user_orders[:limit]

def get_order_details(order_id):
    for order in orders_db:
        if order["id"] == order_id:
            return order
    return None

def cancel_order_in_db(order_id):
    for order in orders_db:
        if order["id"] == order_id:
            order["status"] = "cancelled"
            return order
    return None

def get_order_summary(user_id, start_date, end_date):
    orders = [o for o in orders_db if o["user_id"] == user_id]
    return {"total_orders": len(orders), "user_id": user_id}
