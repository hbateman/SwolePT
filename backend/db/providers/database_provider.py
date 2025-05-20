from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from werkzeug.security import check_password_hash
import csv
from io import StringIO

from ..models.user import User
from ..models.workout import WorkoutHistory

class DatabaseProvider(ABC):
    """Abstract base class for database providers."""
    
    def __init__(self):
        """Initialize the database provider."""
        self._engine = None
        self._session_factory = None
        self._session: Optional[Session] = None
        self._base = declarative_base()
    
    @abstractmethod
    def get_connection_url(self) -> str:
        """Get the database connection URL."""
        pass
    
    def connect(self) -> None:
        """Establish a connection to the database."""
        if self._engine is None:
            connection_url = self.get_connection_url()
            self._engine = create_engine(
                connection_url,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800
            )
            self._session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine
            )
            self._session = self._session_factory()
    
    def disconnect(self) -> None:
        """Close the database connection."""
        if self._session is not None:
            self._session.close()
            self._session = None
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
    
    def init_db(self) -> None:
        """Initialize the database."""
        if self._engine is None:
            self.connect()
        self._base.metadata.create_all(bind=self._engine)
    
    def __enter__(self) -> 'DatabaseProvider':
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """Context manager exit."""
        self.disconnect()
    
    def _validate_user_data(self, username: str, email: str, password_hash: str) -> None:
        """Validate user data before database operations."""
        if not isinstance(username, str) or not username:
            raise ValueError("Username must be a non-empty string")
        if not isinstance(email, str) or not email:
            raise ValueError("Email must be a non-empty string")
        if not isinstance(password_hash, str) or not password_hash:
            raise ValueError("Password hash must be a non-empty string")
    
    def _validate_workout_data(self, workout_data: Dict[str, Any]) -> None:
        """Validate workout data before database operations."""
        required_fields = ['date', 'exercise', 'category']
        for field in required_fields:
            if field not in workout_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(workout_data['date'], (datetime, date)):
            raise ValueError("Date must be a datetime or date object")
        if not isinstance(workout_data['exercise'], str) or not workout_data['exercise']:
            raise ValueError("Exercise must be a non-empty string")
        if not isinstance(workout_data['category'], str) or not workout_data['category']:
            raise ValueError("Category must be a non-empty string")
    
    def create_user(self, username: str, email: str, password_hash: str,
                   given_name: Optional[str] = None,
                   family_name: Optional[str] = None) -> User:
        """Create a new user."""
        if not self._session:
            raise RuntimeError("Database not connected")
        
        try:
            self._validate_user_data(username, email, password_hash)
            
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                given_name=given_name or username,
                family_name=family_name or ""
            )
            
            self._session.add(user)
            self._session.commit()  # Commit the transaction
            self._session.refresh(user)
            return user
                
        except IntegrityError as e:
            self._session.rollback()
            if "users_username_key" in str(e):
                raise ValueError("Username already exists")
            elif "users_email_key" in str(e):
                raise ValueError("Email already exists")
            raise
        except OperationalError as e:
            self._session.rollback()
            raise RuntimeError(f"Database operation failed: {str(e)}")
        except SQLAlchemyError as e:
            self._session.rollback()
            raise RuntimeError(f"Failed to create user: {str(e)}")
        except Exception as e:
            self._session.rollback()
            raise RuntimeError(f"Unexpected error creating user: {str(e)}")
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email address."""
        if not self._session:
            raise RuntimeError("Database not connected")
        
        try:
            return self._session.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to get user")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username."""
        if not self._session:
            raise RuntimeError("Database not connected")
        
        try:
            return self._session.query(User).filter(User.username == username).first()
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to get user")
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a user's password against its hash."""
        return check_password_hash(password_hash, password)
    
    def get_workout_records(self, user_id: str, 
                          start_date: Optional[date] = None,
                          end_date: Optional[date] = None,
                          exercise: Optional[str] = None,
                          category: Optional[str] = None) -> List[WorkoutHistory]:
        """Get workout records for a user with optional filters."""
        if not self._session:
            raise RuntimeError("Database not connected")
        
        try:
            query = self._session.query(WorkoutHistory).filter(WorkoutHistory.user_id == user_id)
            
            if start_date:
                query = query.filter(WorkoutHistory.date >= start_date)
            if end_date:
                query = query.filter(WorkoutHistory.date <= end_date)
            if exercise:
                query = query.filter(WorkoutHistory.exercise == exercise)
            if category:
                query = query.filter(WorkoutHistory.category == category)
            
            records = query.order_by(WorkoutHistory.date.desc(), 
                                   WorkoutHistory.created_at.desc()).all()
            return records
                                
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to get workout records")
    
    @abstractmethod
    def create_workout_record(self, user_id: str, workout_data: Dict[str, Any]) -> WorkoutHistory:
        """Create a new workout record."""
        pass
    
    @abstractmethod
    def update_workout_record(self, record_id: int, workout_data: Dict[str, Any]) -> WorkoutHistory:
        """Update an existing workout record."""
        pass
    
    @abstractmethod
    def delete_workout_record(self, record_id: int) -> bool:
        """Delete a workout record."""
        pass
    
    def process_workout_csv(self, user_id: str, csv_content: str) -> List[Dict[str, Any]]:
        """
        Process a CSV file containing workout data and insert it into the database.
        
        Args:
            user_id (str): The ID of the user uploading the workout data
            csv_content (str): The content of the CSV file as a string
            
        Returns:
            List[Dict[str, Any]]: List of processed workout records as dictionaries
            
        Raises:
            RuntimeError: If database is not connected
            ValueError: If CSV data is invalid
            SQLAlchemyError: If database operation fails
        """
        if not self._session:
            raise RuntimeError("Database not connected")
        
        try:
            # Parse CSV content
            csv_file = StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            # Check required columns
            required_columns = {'date', 'exercise', 'category'}
            optional_columns = {'weight', 'weight_unit', 'reps', 'distance', 'distance_unit', 'time', 'comment'}
            all_columns = required_columns | optional_columns
            
            # Normalize column names (convert to lowercase and replace spaces with underscores)
            def normalize_column_name(col):
                return col.lower().replace(' ', '_')
            
            # Get the actual columns from the CSV and normalize them
            actual_columns = {normalize_column_name(col) for col in reader.fieldnames} if reader.fieldnames else set()
            
            # Check for missing required columns
            missing_columns = required_columns - actual_columns
            if missing_columns:
                raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
            
            # Check for unknown columns
            unknown_columns = actual_columns - all_columns
            if unknown_columns:
                raise ValueError(f"Unknown columns found: {', '.join(unknown_columns)}")
            
            # Create a mapping of normalized column names to actual column names
            column_mapping = {normalize_column_name(col): col for col in reader.fieldnames}
            
            processed_records = []
            
            # Process each row
            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    # Try multiple date formats
                    date_formats = [
                        '%Y-%m-%d',  # 2024-03-14
                        '%m/%d/%Y',  # 03/14/2024
                        '%d/%m/%Y',  # 14/03/2024
                        '%Y/%m/%d',  # 2024/03/14
                        '%m-%d-%Y',  # 03-14-2024
                        '%d-%m-%Y',  # 14-03-2024
                    ]
                    
                    date = None
                    for date_format in date_formats:
                        try:
                            date = datetime.strptime(row[column_mapping['date']], date_format).date()
                            break
                        except ValueError:
                            continue
                    
                    if date is None:
                        raise ValueError(f"Invalid date format in row {row_num}. Supported formats are: YYYY-MM-DD, MM/DD/YYYY, DD/MM/YYYY, YYYY/MM/DD, MM-DD-YYYY, DD-MM-YYYY")
                    
                    # Create workout record with required fields
                    workout_data = {
                        'date': date,
                        'exercise': row[column_mapping['exercise']],
                        'category': row[column_mapping['category']]
                    }
                    
                    # Add optional fields if they exist in the CSV
                    if 'weight' in column_mapping:
                        weight_value = row[column_mapping['weight']]
                        if weight_value and weight_value.strip():
                            workout_data['weight'] = float(weight_value)
                    
                    if 'weight_unit' in column_mapping:
                        workout_data['weight_unit'] = row[column_mapping['weight_unit']]
                    
                    if 'reps' in column_mapping:
                        reps_value = row[column_mapping['reps']]
                        if reps_value and reps_value.strip():
                            workout_data['reps'] = int(reps_value)
                    
                    if 'distance' in column_mapping:
                        distance_value = row[column_mapping['distance']]
                        if distance_value and distance_value.strip():
                            workout_data['distance'] = float(distance_value)
                    
                    if 'distance_unit' in column_mapping:
                        workout_data['distance_unit'] = row[column_mapping['distance_unit']]
                    
                    if 'time' in column_mapping:
                        workout_data['time'] = row[column_mapping['time']]
                    
                    if 'comment' in column_mapping:
                        workout_data['comment'] = row[column_mapping['comment']]
                    
                    # Use existing create_workout_record method
                    record = self.create_workout_record(user_id, workout_data)
                    
                    # Commit the transaction for this record
                    self._session.commit()
                    
                    # Convert record to dictionary
                    record_dict = {
                        'id': record.id,
                        'user_id': record.user_id,
                        'date': record.date.isoformat(),
                        'exercise': record.exercise,
                        'category': record.category,
                        'weight': record.weight,
                        'weight_unit': record.weight_unit,
                        'reps': record.reps,
                        'distance': record.distance,
                        'distance_unit': record.distance_unit,
                        'time': record.time,
                        'comment': record.comment,
                        'created_at': record.created_at.isoformat() if record.created_at else None,
                        'updated_at': record.updated_at.isoformat() if record.updated_at else None
                    }
                    processed_records.append(record_dict)
                    
                except ValueError as e:
                    self._session.rollback()
                    raise ValueError(f"Error in row {row_num}: {str(e)}")
                except Exception as e:
                    self._session.rollback()
                    raise ValueError(f"Error processing row {row_num}: {str(e)}")
            
            return processed_records
                
        except Exception as e:
            self._session.rollback()
            raise RuntimeError(f"Failed to process CSV file: {str(e)}") 