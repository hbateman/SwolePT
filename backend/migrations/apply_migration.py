#!/usr/bin/env python3
import os
import sys
import boto3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from botocore.config import Config
from dotenv import load_dotenv

# Try to load environment variables from .env file
try:
    # Load environment variables from .env file
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    # python-dotenv is not installed, continue without loading .env
    print("python-dotenv not installed, environment variables not loaded from .env file")
except Exception as e:
    # Handle other exceptions when loading .env file
    print(f"Error loading .env file: {str(e)}")

def load_environment():
    """Load environment variables from .env file."""
    # Get the project root directory (two levels up from this script)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(project_root, '.env')
    
    if not os.path.exists(env_path):
        print(f"❌ Error: .env file not found at {env_path}")
        sys.exit(1)
    
    load_dotenv(env_path)
    print("Loaded environment variables from .env file")

def get_db_connection(database_name=None):
    """Get a database connection."""
    try:
        # Use the specified database name or default to environment variable
        db_name = database_name or os.getenv('RDS_DATABASE_NAME')
        
        # For local development, use the current system user
        if os.getenv('LOCAL_DEVELOPMENT', 'true').lower() == 'true':
            conn = psycopg2.connect(
                host=os.getenv('DATABASE_HOST', 'localhost'),
                port=os.getenv('DATABASE_PORT', '5432'),
                user=os.getenv('USER'),  # Use current system user
                password='',  # No password for local development
                database=db_name if database_name else 'postgres',
                sslmode='disable'  # Disable SSL for local development
            )
        else:
            # Production connection
            conn = psycopg2.connect(
                host=os.getenv('DATABASE_HOST'),
                port=os.getenv('DATABASE_PORT'),
                user=os.getenv('RDS_DATABASE_USER'),
                password=os.getenv('RDS_DATABASE_PASSWORD'),
                database=db_name if database_name else 'postgres',
                sslmode='disable'
            )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        return None

def create_database():
    """Create the database if it doesn't exist."""
    try:
        # Connect to default postgres database
        conn = get_db_connection('postgres')
        if not conn:
            return False
        
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (os.getenv('RDS_DATABASE_NAME'),))
        exists = cur.fetchone()
        
        if not exists:
            print(f"Creating database {os.getenv('RDS_DATABASE_NAME')}...")
            cur.execute(f"CREATE DATABASE {os.getenv('RDS_DATABASE_NAME')}")
            print("✅ Database created successfully")
        else:
            print(f"Database {os.getenv('RDS_DATABASE_NAME')} already exists")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error creating database: {str(e)}")
        return False

def apply_migration(migration_file, direction='up'):
    """Apply a migration file."""
    try:
        # Read migration file
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Connect to database
        conn = get_db_connection()
        if not conn:
            print("❌ Failed to connect to database")
            return False
        
        # Execute migration
        cur = conn.cursor()
        
        # Split SQL into statements and execute each one
        statements = sql.split(';')
        for statement in statements:
            if statement.strip():  # Skip empty statements
                try:
                    cur.execute(statement)
                except psycopg2.errors.DuplicateObject:
                    # Skip if object already exists
                    print(f"Note: Object already exists, skipping: {statement[:50]}...")
                    continue
                except Exception as e:
                    print(f"Warning: Error executing statement: {str(e)}")
                    print(f"Statement: {statement[:50]}...")
                    continue
        
        cur.close()
        conn.close()
        
        print(f"✅ Successfully applied {direction} migration: {migration_file}")
        return True
    except Exception as e:
        print(f"❌ Error applying {direction} migration: {str(e)}")
        return False

def main():
    """Main function."""
    # Load environment variables
    load_environment()
    
    # Get migration file from command line arguments
    if len(sys.argv) != 3:
        print("Usage: python apply_migration.py <migration_file> <direction>")
        sys.exit(1)
    
    migration_file = sys.argv[1]
    direction = sys.argv[2]
    
    if not os.path.exists(migration_file):
        print(f"❌ Error: Migration file {migration_file} not found")
        sys.exit(1)
    
    # Create database if it doesn't exist
    print("Creating database if it doesn't exist...")
    if not create_database():
        sys.exit(1)
    
    # Apply migration
    print(f"Applying {direction} migration...")
    if not apply_migration(migration_file, direction):
        sys.exit(1)

if __name__ == '__main__':
    main() 