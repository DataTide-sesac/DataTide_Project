# services/item_crud.py
from sqlalchemy.orm import Session
from DataTide_back.models.item import Item
from DataTide_back.schemas.item import ItemCreate
    # Import 절대경로로 수정
def get_item(db: Session, item_pk: int):
    return db.query(Item).filter(Item.item_pk == item_pk).first()

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Item).offset(skip).limit(limit).all()

def create_item(db: Session, item: ItemCreate):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def create_multiple_items(db: Session, items: list[ItemCreate]):
    db_items = [Item(**item.model_dump()) for item in items]
    db.add_all(db_items)
    db.commit()
    for db_item in db_items:
        db.refresh(db_item)
    return db_items
