"""
User model definition.
"""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from . import Base  # <-- import the shared Base
import uuid

class User(Base):
    __tablename__ = 'users'

    user_id = Column(String(255), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    given_name = Column(String(255), nullable=False)
    family_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 