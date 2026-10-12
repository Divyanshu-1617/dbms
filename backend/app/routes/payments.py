from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import PaymentCreate, PaymentResponse
from ..services import get_payments_for_booking, create_payment

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.get("/booking/{booking_id}", response_model=List[PaymentResponse])
def list_payments_for_booking(booking_id: str):
    return get_payments_for_booking(booking_id)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def make_payment(payment_data: PaymentCreate):
    """
    Process rental, deposit, refund, or penalty payment.
    Calculates platform commission and owner earnings.
    """
    try:
        return create_payment(payment_data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
