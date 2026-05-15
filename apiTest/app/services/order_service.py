from app.db import orders_db, products_db
from app.utils.helpers import calculate_discount

def create_order_in_db(user_id, items):
    # TODO: validate user_id exists
    total = 0
    # Duplicate logic smell: calculating total inside here instead of a separate method
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
            
    # duplicate logic for discount
    if total > 1000:
        disc = total * (10/100)
        total = total - disc
        
    order_id = len(orders_db) + 1
    new_order = {
        "id": order_id,
        "user_id": user_id,
        "items": [{"product_id": i.product_id, "quantity": i.quantity} for i in items],
        "total_price": total,
        "status": "created"
    }
    orders_db.append(new_order)
    return new_order

def get_orders_by_user(user_id):
    user_orders = []
    for order in orders_db:
        if order["user_id"] == user_id:
            user_orders.append(order)
    return user_orders

def get_order_details(order_id):
    for order in orders_db:
        if order["id"] == order_id:
            return order
    return None

def cancel_order_in_db(order_id):
    # FIXME: this doesn't restore stock!
    for order in orders_db:
        if order["id"] == order_id:
            order["status"] = "cancelled"
            return order
    return None
