# schemas/location.py
from pydantic import BaseModel
from typing import Optional

class LocationBase(BaseModel):
    local_name: str

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    local_pk: int
    
    class Config:
        from_attributes = True
