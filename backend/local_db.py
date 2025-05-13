import os
import psycopg2
from psycopg2.extras import RealDictCursor, DictCursor
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from io import StringIO
from datetime import datetime

def get_db_connection():
    """Get a connection to the local PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=os.getenv('DATABASE_PORT', '5432'),
            database='swolept',  # Use our local database name
            user=os.getenv('DB_USER', os.getenv('USER')),  # Default to system user
            password=os.getenv('DB_PASSWORD', '')  # Empty password for local development
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

def verify_db_ready():
    """Verify that the database is ready for use."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if required tables exist
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'workout_history')
            );
        """)
        
        tables_exist = cursor.fetchone()[0]
        if not tables_exist:
            raise Exception("Required database tables do not exist. Please run migrations first.")
        
        return True
    except Exception as e:
        print(f"Database verification failed: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def init_db():
    """Initialize the database with required tables."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Read and execute the initial schema
        with open('migrations/001_initial_schema.sql', 'r') as f:
            sql = f.read()
            
            # Split the SQL into individual statements
            statements = sql.split(';')
            
            # Execute each statement separately
            for statement in statements:
                if statement.strip():  # Skip empty statements
                    try:
                        cursor.execute(statement)
                    except psycopg2.errors.DuplicateObject:
                        # Skip if object already exists
                        continue
                    except Exception as e:
                        print(f"Warning: Error executing statement: {str(e)}")
                        continue
        
        conn.commit()
        print("Database initialized successfully!")
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def create_user(email, password):
    """Create a new user in the database."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return None, "User already exists"
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
            (email, password_hash)
        )
        user_id = cursor.fetchone()['id']
        
        conn.commit()
        return user_id, None
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error creating user: {str(e)}")
        return None, str(e)
    finally:
        if conn:
            conn.close()

def get_user(email):
    """Get a user from the database by email."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def verify_password(user, password):
    """Verify a user's password."""
    return check_password_hash(user['password_hash'], password)

def process_workout_csv(user_id: str, csv_content: str) -> list:
    """
    Process a CSV file containing workout data and store it in the database.
    Returns a list of processed workout records.
    """
    conn = None
    try:
        conn = get_db_connection()
        # Create a CSV reader from the string content
        csv_file = StringIO(csv_content)
        reader = csv.DictReader(csv_file)
        
        # Prepare the insert statement
        insert_stmt = """
            INSERT INTO workout_history (
                user_id, date, exercise, category, weight, weight_unit,
                reps, distance, distance_unit, time, comment
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id
        """
        
        processed_records = []
        with conn.cursor() as cur:
            for row in reader:
                # Convert empty strings to None
                weight = float(row['Weight']) if row['Weight'] else None
                reps = int(row['Reps']) if row['Reps'] else None
                distance = float(row['Distance']) if row['Distance'] else None
                
                # Insert the record
                cur.execute(insert_stmt, (
                    user_id,
                    datetime.strptime(row['Date'], '%Y-%m-%d').date(),
                    row['Exercise'],
                    row['Category'],
                    weight,
                    row['Weight Unit'] or None,
                    reps,
                    distance,
                    row['Distance Unit'] or None,
                    row['Time'] or None,
                    row['Comment'] or None
                ))
                
                workout_id = cur.fetchone()[0]
                processed_records.append({
                    'id': workout_id,
                    'date': row['Date'],
                    'exercise': row['Exercise'],
                    'category': row['Category'],
                    'weight': weight,
                    'weight_unit': row['Weight Unit'],
                    'reps': reps,
                    'distance': distance,
                    'distance_unit': row['Distance Unit'],
                    'time': row['Time'],
                    'comment': row['Comment']
                })
        
        conn.commit()
        return processed_records
        
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Error processing workout CSV: {str(e)}")
    finally:
        if conn:
            conn.close() 