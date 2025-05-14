"""
Database models package for SwolePT backend.
This package contains all SQLAlchemy model definitions.
"""

from .user import User
from .workout import WorkoutHistory

__all__ = ['User', 'WorkoutHistory'] 