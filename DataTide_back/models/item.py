from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base

class Item(Base):
    __tablename__ = "item"

    item_pk = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(20))

    # Relationship to item_retail
    item_retail = relationship("ItemRetail", back_populates="item")