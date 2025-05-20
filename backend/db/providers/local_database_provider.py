import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

from .database_provider import DatabaseProvider
from ..models.workout import WorkoutHistory

class LocalDatabaseProvider(DatabaseProvider):
    """Local PostgreSQL database provider."""
    
    def get_connection_url(self) -> str:
        """Get the local PostgreSQL connection URL."""
        return "postgresql://postgres:postgres@localhost:5432/swolept"
    
    def create_workout_record(self, user_id: str, workout_data: Dict[str, Any]) -> WorkoutHistory:
        """Create a new workout record."""
        if not self._session:
            raise RuntimeError("Database not connected")
        
        try:
            self._validate_workout_data(workout_data)
            
            record = WorkoutHistory(
                user_id=user_id,
                date=workout_data['date'],
                exercise=workout_data['exercise'],
                category=workout_data['category'],
                weight=workout_data.get('weight'),
                weight_unit=workout_data.get('weight_unit'),
                reps=workout_data.get('reps'),
                distance=workout_data.get('distance'),
                distance_unit=workout_data.get('distance_unit'),
                time=workout_data.get('time'),
                comment=workout_data.get('comment')
            )
            
            self._session.add(record)
            self._session.flush()
            self._session.refresh(record)
            return record
                
        except IntegrityError as e:
            self._session.rollback()
            raise ValueError("Failed to create workout record")
        except OperationalError as e:
            self._session.rollback()
            raise RuntimeError("Database operation failed")
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError("Failed to create workout record")
    
    def update_workout_record(self, record_id: int, workout_data: Dict[str, Any]) -> WorkoutHistory:
        """Update an existing workout record."""
        if not self._session:
            raise RuntimeError("Database not connected")
        
        try:
            record = self._session.query(WorkoutHistory).filter(WorkoutHistory.id == record_id).first()
            if not record:
                raise ValueError("Workout record not found")
            
            self._validate_workout_data(workout_data)
            
            record.date = workout_data['date']
            record.exercise = workout_data['exercise']
            record.category = workout_data['category']
            record.weight = workout_data.get('weight')
            record.weight_unit = workout_data.get('weight_unit')
            record.reps = workout_data.get('reps')
            record.distance = workout_data.get('distance')
            record.distance_unit = workout_data.get('distance_unit')
            record.time = workout_data.get('time')
            record.comment = workout_data.get('comment')
            record.updated_at = datetime.utcnow()
            
            self._session.flush()
            self._session.refresh(record)
            return record
                
        except IntegrityError as e:
            self._session.rollback()
            raise ValueError("Failed to update workout record")
        except OperationalError as e:
            self._session.rollback()
            raise RuntimeError("Database operation failed")
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError("Failed to update workout record")
    
    def delete_workout_record(self, record_id: int) -> bool:
        """Delete a workout record."""
        if not self._session:
            raise RuntimeError("Database not connected")
        
        try:
            record = self._session.query(WorkoutHistory).filter(WorkoutHistory.id == record_id).first()
            if not record:
                raise ValueError("Workout record not found")
            
            self._session.delete(record)
            self._session.flush()
            return True
                
        except IntegrityError as e:
            self._session.rollback()
            raise ValueError("Failed to delete workout record")
        except OperationalError as e:
            self._session.rollback()
            raise RuntimeError("Database operation failed")
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError("Failed to delete workout record") 