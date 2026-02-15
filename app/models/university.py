from sqlalchemy import Column, Integer, String, Numeric
from app.core.db import Base 


class University(Base):
    __tablename__ = "universities"
    
    
    id = Column(Integer, primary_key = True, index = True)
    name = Column(String, unique = True, nullable = False)
    latitude = Column(Numeric(10,8))
    longitude = Column(Numeric(11,8))