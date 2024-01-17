from sqlalchemy import Boolean, Column, Integer, String, Text
from database import Base


class Assign(Base):
    __tablename__ = 'assigns'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(Text)
    isvideo = Column(Boolean)
    time = Column(String(20))
