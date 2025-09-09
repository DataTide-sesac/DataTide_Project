from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from DataTide_back.services import location_crud
from DataTide_back.schemas.location import Location, LocationCreate
from DataTide_back.core.database import get_db

router = APIRouter(prefix="/locations", tags=["locations"])

@router.post("/", response_model=Location)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    db_location = location_crud.get_location_by_name(db, local_name=location.local_name)
    if db_location:
        raise HTTPException(status_code=400, detail="Location name already registered")
    return location_crud.create_location(db=db, location=location)

@router.get("/", response_model=List[Location])
def read_locations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    locations = location_crud.get_locations(db, skip=skip, limit=limit)
    return locations

@router.get("/{local_pk}", response_model=Location)
def read_location(local_pk: int, db: Session = Depends(get_db)):
    db_location = location_crud.get_location(db, local_pk=local_pk)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location
