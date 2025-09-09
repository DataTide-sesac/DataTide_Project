from sqlalchemy.orm import Session
from DataTide_back.db.models.location import Location
from DataTide_back.schemas.location import LocationCreate

def get_location(db: Session, local_pk: int):
    return db.query(Location).filter(Location.local_pk == local_pk).first()

def get_location_by_name(db: Session, local_name: str):
    return db.query(Location).filter(Location.local_name == local_name).first()

def get_locations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Location).offset(skip).limit(limit).all()

def create_location(db: Session, location: LocationCreate):
    db_location = Location(local_name=location.local_name)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location
