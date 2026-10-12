from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import InspectionCreate, InspectionResponse
from ..services import get_inspections_for_booking, create_inspection

router = APIRouter(prefix="/api/inspections", tags=["Inspections"])


@router.get("/booking/{booking_id}", response_model=List[InspectionResponse])
def list_inspections_for_booking(booking_id: str):
    return get_inspections_for_booking(booking_id)


@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
def record_inspection(insp_data: InspectionCreate):
    """
    Records vehicle inspection at Pickup or Return.
    """
    try:
        return create_inspection(insp_data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
