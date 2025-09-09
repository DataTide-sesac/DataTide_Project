from sqlalchemy.orm import Session
from DataTide_back.db.models.item_retail import ItemRetail
from DataTide_back.schemas.item_retail import ItemRetailCreate
from DataTide_back.db.models.item import Item # To look up item_pk

def get_item_retail(db: Session, retail_pk: int):
    return db.query(ItemRetail).filter(ItemRetail.retail_pk == retail_pk).first()

def get_item_retails(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ItemRetail).offset(skip).limit(limit).all()

def create_item_retail(db: Session, item_retail: ItemRetailCreate):
    # Look up item_pk from item_name
    item = db.query(Item).filter(Item.item_name == item_retail.item_name).first()
    if not item:
        # This should ideally be handled by the router with an HTTPException
        return None # Or raise a specific error

    db_item_retail = ItemRetail(
        item_pk=item.item_pk,
        production=item_retail.production,
        inbound=item_retail.inbound,
        sales=item_retail.sales,
        month_date=item_retail.month_date
    )
    db.add(db_item_retail)
    db.commit()
    db.refresh(db_item_retail)
    return db_item_retail
