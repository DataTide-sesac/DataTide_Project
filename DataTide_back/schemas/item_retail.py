from pydantic import BaseModel
from datetime import date
from typing import Optional

class ItemRetailBase(BaseModel):
    production: int
    inbound: int
    sales: int
    month_date: date

class ItemRetailCreate(ItemRetailBase):
    item_name: str # For creation, we'll use item_name

class ItemRetail(ItemRetailBase):
    retail_pk: int
    item_pk: int # For response, we'll have item_pk

    class Config:
        from_attributes = True
