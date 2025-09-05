# schemas/item.py
from pydantic import BaseModel
from typing import List

class ItemBase(BaseModel):
    item_name: str

class ItemCreate(ItemBase):
    pass

class ItemCreateList(BaseModel):
    items: List[ItemCreate]

class Item(ItemBase):
    item_pk: int  # id -> item_pk 변경

    class Config:
        from_attributes = True # SQLAlchemy 모델과 호환되도록 설정
