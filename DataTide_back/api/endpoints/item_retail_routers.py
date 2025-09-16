from fastapi import APIRouter, HTTPException, status
from typing import List

from services import item_retail_crud
from schemas.item_retail import ItemRetail, ItemRetailCreate

router = APIRouter(prefix="/item_retails", tags=["item_retails"])

@router.post("/", response_model=ItemRetail)
def create_item_retail(item_retail: ItemRetailCreate):
    db_item_retail = item_retail_crud.create_item_retail(item_retail=item_retail)
    if db_item_retail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with name '{item_retail.item_name}' not found."
        )
    return db_item_retail

@router.get("/", response_model=List[ItemRetail])
def read_item_retails(skip: int = 0, limit: int = 100):
    item_retails = item_retail_crud.get_item_retails(skip=skip, limit=limit)
    return item_retails

@router.get("/{retail_pk}", response_model=ItemRetail)
def read_item_retail(retail_pk: int):
    db_item_retail = item_retail_crud.get_item_retail(retail_pk=retail_pk)
    if db_item_retail is None:
        raise HTTPException(status_code=404, detail="ItemRetail not found")
    return db_item_retail
