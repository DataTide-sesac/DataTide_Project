from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from services import item_crud
from schemas.item import Item, ItemCreate
from core.database import get_db

router = APIRouter()

@router.post("/", response_model=Item)
def create_new_item(item: ItemCreate, db: Session = Depends(get_db)):
    return item_crud.create_item(db=db, item=item)

@router.get("/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = item_crud.get_items(db, skip=skip, limit=limit)
    return items

@router.get("/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = item_crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
