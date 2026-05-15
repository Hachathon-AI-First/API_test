from fastapi import APIRouter, HTTPException
from app.models.schemas import OrderCreate, Order
from app.services.order_service import create_order_in_db, get_orders_by_user, get_order_details, cancel_order_in_db

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/")
def create_order(order: OrderCreate):
    # sync endpoint simulating legacy blocking call
    result = create_order_in_db(order.user_id, order.items)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/user/{user_id}")
def list_orders(user_id: int):
    return get_orders_by_user(user_id)

@router.get("/{order_id}")
def order_details(order_id: int):
    order = get_order_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.delete("/{order_id}")
def cancel_order(order_id: int):
    order = cancel_order_in_db(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order cancelled", "order": order}
