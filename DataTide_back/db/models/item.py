# models/item.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from DataTide_back.core.database import Base
from DataTide_back.db.models.item_retail import ItemRetail
     #Import 절대경로로 수정
class Item(Base):
    __tablename__ = "item"

    # 문자열로 참조하여 순환 임포트 방지
    item_pk = Column(Integer, primary_key=True, autoincrement=True)
    item_name = Column(String(20))

    item_retail = relationship(ItemRetail, back_populates="item")
     
