from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from ..models import MaintenanceCreate, MaintenanceResponse, MaintenanceCompleteRequest
from ..services import get_maintenance_history, create_maintenance_record, complete_maintenance_record

router = APIRouter(prefix="/api/maintenance", tags=["Maintenance"])


@router.get("", response_model=List[MaintenanceResponse])
def list_maintenance(vehicle_id: Optional[str] = Query(None, description="Filter by vehicle ID")):
    return get_maintenance_history(vehicle_id=vehicle_id)


@router.post("", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
def start_maintenance(m_data: MaintenanceCreate):
    """
    Log vehicle maintenance and immediately block it from new bookings (Scenario 9.5).
    """
    try:
        return create_maintenance_record(m_data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{maintenance_id}/complete", response_model=MaintenanceResponse)
def finish_maintenance(maintenance_id: str, req: MaintenanceCompleteRequest):
    """
    Complete maintenance and restore vehicle availability (Scenario 9.5).
    """
    try:
        return complete_maintenance_record(maintenance_id, req.cost)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
