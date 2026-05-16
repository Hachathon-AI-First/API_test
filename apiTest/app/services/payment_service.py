from app.db import payments_db, orders_db

def process_payment_for_order(order_id, amount, method, currency="BRL", metadata=None):
    order = next((o for o in orders_db if o["id"] == order_id), None)

    if not order:
        return {"status": "failed", "reason": "Order not found"}

    if order["status"] == "cancelled":
        return {"status": "failed", "reason": "Order is cancelled"}

    if amount < order["total_price"]:
        return {"status": "failed", "reason": "Insufficient amount"}

    payment_id = len(payments_db) + 1
    payment = {
        "id": payment_id,
        "order_id": order_id,
        "amount": amount,
        "method": method,
        "currency": currency,
        "metadata": metadata or {},
        "status": "success"
    }
    payments_db.append(payment)
    order["status"] = "paid"
    return payment

def get_payment_by_id(payment_id):
    return next((p for p in payments_db if p["id"] == payment_id), None)
