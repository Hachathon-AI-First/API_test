from app.db import payments_db, orders_db

def process_payment_for_order(order_id, amount, method):
    # missing type hints and docstrings
    # no try/except for finding order
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
        "status": "success"
    }
    payments_db.append(payment)
    
    # update order status
    order["status"] = "paid"
    
    return payment

def refund_payment_service(payment_id):
    # this might raise StopIteration if next() is called differently, but let's just do a basic loop
    payment = None
    for p in payments_db:
        if p["id"] == payment_id:
            payment = p
            break
            
    if not payment:
        # dict returned directly
        return {"error": "payment not found"}
        
    if payment["status"] == "refunded":
        return {"error": "already refunded"}
        
    payment["status"] = "refunded"
    
    # Update related order
    for o in orders_db:
        if o["id"] == payment["order_id"]:
            o["status"] = "refunded"
            break
            
    return payment
