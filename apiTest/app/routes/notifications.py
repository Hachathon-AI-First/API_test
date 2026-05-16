from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.notification_service import (
    send_order_confirmation,
    send_payment_receipt,
    send_shipping_update,
    send_refund_confirmation,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])

class ShippingUpdateRequest(BaseModel):
    user_id: int
    order_id: int
    tracking_code: str

@router.post("/order-confirmation/{user_id}/{order_id}")
def order_confirmation(user_id: int, order_id: int):
    result = send_order_confirmation(user_id, order_id)
    if result["status"] == "failed":
        raise HTTPException(status_code=404, detail=result["reason"])
    return result

@router.post("/payment-receipt/{user_id}/{payment_id}")
def payment_receipt(user_id: int, payment_id: int, amount: float):
    result = send_payment_receipt(user_id, payment_id, amount)
    if result["status"] == "failed":
        raise HTTPException(status_code=404, detail=result["reason"])
    return result

@router.post("/shipping-update")
def shipping_update(request: ShippingUpdateRequest):
    result = send_shipping_update(request.user_id, request.order_id, request.tracking_code)
    if result["status"] == "failed":
        raise HTTPException(status_code=404, detail=result["reason"])
    return result

@router.post("/refund-confirmation/{user_id}/{payment_id}")
def refund_confirmation(user_id: int, payment_id: int, amount: float):
    result = send_refund_confirmation(user_id, payment_id, amount)
    if result["status"] == "failed":
        raise HTTPException(status_code=404, detail=result["reason"])
    return result
