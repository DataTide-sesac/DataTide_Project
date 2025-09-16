from sqlalchemy import Column, BigInteger, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class ItemRetail(Base):
    __tablename__ = "item_retail"

    retail_pk = Column(BigInteger, primary_key=True, autoincrement=True)
    item_pk = Column(Integer, ForeignKey("item.item_pk"))
    production = Column(Integer)
    inbound = Column(Integer)
    sales = Column(Integer)
    month_date = Column(Date)

    # Relationship to item
    item = relationship("Item", back_populates="item_retail")