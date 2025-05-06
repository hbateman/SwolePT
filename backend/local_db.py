import os
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    """Get a connection to the local PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=os.getenv('DATABASE_PORT', '5432'),
            database=os.getenv('RDS_DATABASE_NAME'),
            user=os.getenv('RDS_DATABASE_USER'),
            password=os.getenv('RDS_DATABASE_PASSWORD')
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

def init_db():
    """Initialize the database with required tables."""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
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