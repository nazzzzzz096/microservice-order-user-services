from sqlalchemy import Column, Integer, String
import database

Base = database.Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    product = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False)