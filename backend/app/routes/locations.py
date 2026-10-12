from fastapi import APIRouter, HTTPException, status
from typing import List
from ..models import LocationCreate, LocationResponse
from ..services import get_all_locations, create_location

router = APIRouter(prefix="/api/locations", tags=["Locations"])


@router.get("", response_model=List[LocationResponse])
def list_locations():
    return get_all_locations()


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def add_location(loc_data: LocationCreate):
    return create_location(loc_data.model_dump())
