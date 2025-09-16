# api/endpoints/location_routers.py
from fastapi import APIRouter, HTTPException
from typing import List
from services import location_crud
from schemas.location import Location, LocationCreate

router = APIRouter(prefix="/locations", tags=["locations"])

@router.post("/", response_model=Location)
def create_location(location: LocationCreate):
    db_location = location_crud.get_location_by_name(local_name=location.local_name)
    if db_location:
        raise HTTPException(status_code=400, detail="Location name already registered")
    return location_crud.create_location(location=location)

@router.get("/", response_model=List[Location])
def read_locations(skip: int = 0, limit: int = 100):
    locations = location_crud.get_locations(skip=skip, limit=limit)
    return locations

@router.get("/{local_pk}", response_model=Location)
def read_location(local_pk: int):
    db_location = location_crud.get_location_by_pk(local_pk=local_pk)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location
