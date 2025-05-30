"""
WorkoutHistory model definition.
"""
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from . import Base  # <-- import the shared Base

class WorkoutHistory(Base):
    __tablename__ = 'workout_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey('users.user_id'), nullable=False)
    date = Column(Date, nullable=False)
    exercise = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    weight = Column(Float)
    weight_unit = Column(String(10))
    reps = Column(Integer)
    distance = Column(Float)
    distance_unit = Column(String(10))
    time = Column(String(50))
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 