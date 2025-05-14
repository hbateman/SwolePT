import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import csv
from io import StringIO
import time
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='workout_upload.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_db_connection():
    """Get a database connection."""
    return psycopg2.connect(
        host=os.getenv('DATABASE_HOST'),
        port=os.getenv('DATABASE_PORT'),
        user=os.getenv('RDS_DATABASE_USER'),
        password=os.getenv('RDS_DATABASE_PASSWORD'),
        database=os.getenv('RDS_DATABASE_NAME')
    )

def create_user(username, email, password):
    """Create a new user."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id",
        (username, email, password)
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id

def get_user(username):
    """Get a user by username."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def verify_password(username, password):
    """Verify a user's password."""
    user = get_user(username)
    if user and user['password'] == password:  # In production, use proper password hashing
        return True
    return False

def verify_db_ready():
    """Verify that the database is ready to accept connections."""
    max_attempts = 30
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            conn = get_db_connection()
            conn.close()
            return True
        except psycopg2.OperationalError:
            print(f"Waiting for database to be ready (attempt {attempt}/{max_attempts})...")
            time.sleep(2)
            attempt += 1
    
    raise Exception("Database failed to become ready after maximum attempts")

def process_workout_csv(user_id, csv_content):
    """Process a CSV file containing workout data and store it in the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    processed_records = []
    
    try:
        # Parse CSV content
        csv_file = StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Create case-insensitive mapping of column names
        column_mapping = {col.lower(): col for col in reader.fieldnames}
        logging.info(f"CSV Headers: {reader.fieldnames}")
        logging.info(f"Column mapping: {column_mapping}")
        
        # Validate required columns
        required_columns = ['date', 'exercise', 'category']
        row_number = 1  # Start counting from 1 for human-readable line numbers
        
        for row in reader:
            has_error = False
            error_details = []
            
            # Check for required fields using case-insensitive mapping
            missing_fields = []
            for req_col in required_columns:
                if req_col not in column_mapping or not row.get(column_mapping[req_col]):
                    missing_fields.append(req_col)
            
            if missing_fields:
                has_error = True
                error_details.append(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Convert date string to proper format if needed
            try:
                date = row.get(column_mapping.get('date', 'date'))
                if not isinstance(date, str):
                    has_error = True
                    error_details.append(f"Date must be a string, got {type(date)}")
            except Exception as e:
                has_error = True
                error_details.append(f"Invalid date format: {str(e)}")
            
            if has_error:
                error_msg = f"\nError in row {row_number}:\nRow data: {row}\nIssues: {'; '.join(error_details)}"
                logging.error(error_msg)
                print(error_msg)  # Also print to console
                raise ValueError(f"Row {row_number}: {'; '.join(error_details)}")
            
            try:
                # Helper function to convert empty strings to None for numeric fields
                def get_numeric_value(value):
                    if value == '':
                        return None
                    try:
                        return float(value) if '.' in str(value) else int(value)
                    except (ValueError, TypeError):
                        return None

                # Get values with proper type conversion
                weight = get_numeric_value(row.get(column_mapping.get('weight', 'weight')))
                reps = get_numeric_value(row.get(column_mapping.get('reps', 'reps')))
                distance = get_numeric_value(row.get(column_mapping.get('distance', 'distance')))
                
                # Insert workout record using case-insensitive mapping
                cur.execute("""
                    INSERT INTO workout_history (
                        user_id, date, exercise, category,
                        weight, weight_unit, reps,
                        distance, distance_unit, time, comment
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    user_id,
                    row.get(column_mapping.get('date', 'date')),  # Required
                    row.get(column_mapping.get('exercise', 'exercise')),  # Required
                    row.get(column_mapping.get('category', 'category')),  # Required
                    weight,  # Converted to float or None
                    row.get(column_mapping.get('weight unit', 'weight_unit')),
                    reps,  # Converted to int or None
                    distance,  # Converted to float or None
                    row.get(column_mapping.get('distance unit', 'distance_unit')),
                    row.get(column_mapping.get('time', 'time')),
                    row.get(column_mapping.get('comment', 'comment'))
                ))
                
                record_id = cur.fetchone()[0]
                processed_records.append({
                    'id': record_id,
                    'date': row.get(column_mapping.get('date', 'date')),
                    'exercise': row.get(column_mapping.get('exercise', 'exercise')),
                    'category': row.get(column_mapping.get('category', 'category'))
                })
                
            except Exception as e:
                error_msg = f"\nDatabase error in row {row_number}:\nRow data: {row}\nError: {str(e)}"
                logging.error(error_msg)
                print(error_msg)  # Also print to console
                raise ValueError(f"Row {row_number}: Database error: {str(e)}")
            
            row_number += 1
        
        conn.commit()
        success_msg = f"Successfully processed {len(processed_records)} records"
        logging.info(success_msg)
        return processed_records
        
    except Exception as e:
        conn.rollback()
        error_msg = f"Error processing CSV: {str(e)}"
        logging.error(error_msg)
        print(error_msg)  # Also print to console
        raise ValueError(error_msg)
    finally:
        cur.close()
        conn.close() 