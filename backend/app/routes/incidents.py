from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import IncidentCreate, IncidentResponse, IncidentResolveRequest
from ..services import get_all_incidents, get_incidents_for_booking, create_incident, resolve_incident

router = APIRouter(prefix="/api/incidents", tags=["Damage & Incidents"])


@router.get("", response_model=List[IncidentResponse])
def list_incidents():
    return get_all_incidents()


@router.get("/booking/{booking_id}", response_model=List[IncidentResponse])
def list_incidents_for_booking(booking_id: str):
    return get_incidents_for_booking(booking_id)


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def report_incident(incident_data: IncidentCreate):
    """
    Owner or Admin reports damage or late return penalty (Scenarios 9.4, 9.7).
    """
    try:
        return create_incident(incident_data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{incident_id}/resolve", response_model=IncidentResponse)
def adjudicate_incident(incident_id: str, req: IncidentResolveRequest):
    """
    Admin resolves dispute: 'Upheld', 'Waived', or 'Resolved' (Scenario 9.11).
    """
    return resolve_incident(incident_id, req.resolution_status)
