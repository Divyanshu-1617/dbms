from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from ..models import VehicleCreate, VehicleResponse, VehicleStatusUpdate
from ..services import get_all_vehicles, get_vehicle_by_id, create_vehicle, update_vehicle_status

router = APIRouter(prefix="/api/vehicles", tags=["Vehicles"])


@router.get("", response_model=List[VehicleResponse])
def list_vehicles(
    city: Optional[str] = Query(None, description="Filter by city, e.g. Manali, Shimla"),
    status: Optional[str] = Query(None, description="Filter by vehicle status, e.g. Available, Booked, Under Maintenance"),
):
    return get_all_vehicles(city=city, status=status)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: str):
    veh = get_vehicle_by_id(vehicle_id)
    if not veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return veh


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def register_vehicle(veh_data: VehicleCreate):
    try:
        return create_vehicle(veh_data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{vehicle_id}/status", response_model=VehicleResponse)
def set_vehicle_status(vehicle_id: str, req: VehicleStatusUpdate):
    veh = get_vehicle_by_id(vehicle_id)
    if not veh:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    update_vehicle_status(vehicle_id, req.vehicle_status)
    return get_vehicle_by_id(vehicle_id)
