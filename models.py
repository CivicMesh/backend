from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Text, Float, Table, UniqueConstraint, Index, func, Enum, LargeBinary
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    subcategory = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)