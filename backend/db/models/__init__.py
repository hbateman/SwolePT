"""
Database models package for SwolePT backend.
This package contains all SQLAlchemy model definitions.
"""

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from .user import User
from .workout import WorkoutHistory

__all__ = ['Base', 'User', 'WorkoutHistory'] 