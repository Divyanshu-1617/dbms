from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from ..models import BookingCreate, BookingResponse, BookingDecision, BookingCancel
from ..services import (
    get_all_bookings,
    get_booking_by_id,
    create_booking_request,
    update_booking_status,
)

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])


@router.get("", response_model=List[BookingResponse])
def list_bookings(
    tourist_id: Optional[str] = Query(None, description="Filter bookings made by tourist"),
    owner_id: Optional[str] = Query(None, description="Filter bookings for vehicles owned by owner"),
):
    return get_all_bookings(tourist_id=tourist_id, owner_id=owner_id)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: str):
    b = get_booking_by_id(booking_id)
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    return b


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def request_booking(b_data: BookingCreate):
    """
    Tourist creates a booking request.
    Handles overlap check and maintenance check automatically.
    """
    try:
        booking, warning = create_booking_request(b_data.model_dump())
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{booking_id}/decision", response_model=BookingResponse)
def owner_decision(booking_id: str, decision: BookingDecision):
    """
    Owner approves or rejects a booking request (Scenario 9.1 & 9.2).
    """
    try:
        return update_booking_status(
            booking_id=booking_id,
            new_status=decision.booking_status,
            cancellation_reason=decision.cancellation_reason,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(booking_id: str, cancel: BookingCancel):
    """
    Tourist cancels a booking prior to pickup (Scenario 9.6).
    """
    b = get_booking_by_id(booking_id)
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    if b["booking_status"] in ("Completed", "Cancelled", "Rejected"):
        raise HTTPException(status_code=400, detail=f"Cannot cancel booking with status '{b['booking_status']}'")

    return update_booking_status(
        booking_id=booking_id,
        new_status="Cancelled",
        cancellation_reason=cancel.cancellation_reason,
    )
