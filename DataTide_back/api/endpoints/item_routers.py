# routers/items.py
from fastapi import APIRouter, HTTPException
from typing import List

from services import item_crud
from schemas.item import Item, ItemCreate, ItemCreateList

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=Item)
def create_new_item(item: ItemCreate):
    return item_crud.create_item(item=item)

@router.post("/bulk", response_model=List[Item])
def create_bulk_items(item_list: ItemCreateList):
    created_items = item_crud.create_multiple_items(items=item_list.items)
    return created_items

@router.get("/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100):
    items = item_crud.get_items(skip=skip, limit=limit)
    return items

@router.get("/{item_pk}", response_model=Item)
def read_item(item_pk: int):
    db_item = item_crud.get_item(item_pk=item_pk)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item
