from app.db import users_db

def send_order_confirmation(user_id: int, order_id: int) -> dict:
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"status": "failed", "reason": "User not found"}

    return {
        "status": "sent",
        "to": user.get("email"),
        "template": "order_confirmation",
        "order_id": order_id
    }

def send_payment_receipt(user_id: int, payment_id: int, amount: float) -> dict:
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"status": "failed", "reason": "User not found"}

    return {
        "status": "sent",
        "to": user.get("email"),
        "template": "payment_receipt",
        "payment_id": payment_id,
        "amount": amount
    }

def send_shipping_update(user_id: int, order_id: int, tracking_code: str) -> dict:
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"status": "failed", "reason": "User not found"}

    return {
        "status": "sent",
        "to": user.get("email"),
        "template": "shipping_update",
        "order_id": order_id,
        "tracking_code": tracking_code
    }

def send_refund_confirmation(user_id: int, payment_id: int, amount: float) -> dict:
    user = next((u for u in users_db if u["id"] == user_id), None)
    if not user:
        return {"status": "failed", "reason": "User not found"}

    return {
        "status": "sent",
        "to": user.get("email"),
        "template": "refund_confirmation",
        "payment_id": payment_id,
        "amount": amount
    }
