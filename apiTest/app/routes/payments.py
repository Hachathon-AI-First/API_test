from fastapi import APIRouter, Request, Header
from app.services.payment_service import process_payment_for_order, refund_payment_service

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/process")
def process_payment(request: Request, order_id: int, amount: float, method: str = "credit_card", x_custom_header: str = Header(None)):
    # Relies on request context and headers in a confusing way, making it a bad MCP tool
    if x_custom_header == "debug":
        print("Debug mode payment")
        
    result = process_payment_for_order(order_id, amount, method)
    return result

@router.post("/refund/{payment_id}")
def refund_payment(payment_id: int):
    # no typed response, missing try/except
    result = refund_payment_service(payment_id)
    if "error" in result:
        return {"status": "error", "message": result["error"]}
    return {"status": "success", "payment": result}
