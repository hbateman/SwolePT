#!/usr/bin/env python3
import os
import sys
import boto3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from botocore.config import Config

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    # python-dotenv is not installed, continue without loading .env
    print("python-dotenv not installed, environment variables not loaded from .env file")
except Exception as e:
    # Handle other exceptions when loading .env file
    print(f"Error loading .env file: {str(e)}")

def get_db_connection():
    """
    Get a connection to the RDS database using IAM authentication
    """
    try:
        # Get database connection details from environment variables
        host = os.environ.get('DATABASE_HOST')
        port = os.environ.get('DATABASE_PORT', '5432')
        database = os.environ.get('DATABASE_NAME')
        user = os.environ.get('DATABASE_USER')
        region = os.environ.get('AWS_REGION', 'ap-southeast-2')

        # Check if required environment variables are set
        required_vars = ['DATABASE_HOST', 'DATABASE_NAME', 'DATABASE_USER']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Create an RDS client
        rds_client = boto3.client(
            'rds',
            region_name=region,
            config=Config(signature_version='v4')
        )

        # Generate an authentication token
        auth_token = rds_client.generate_db_auth_token(
            DBHostname=host,
            Port=int(port),
            DBUsername=user,
            Region=region
        )

        # Create connection
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=auth_token,
            sslmode='require'
        )
        
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

def apply_migration(migration_file, direction="up"):
    """
    Apply a migration file to the database
    
    Args:
        migration_file (str): Path to the migration file
        direction (str): Either "up" or "down" to indicate migration direction
    """
    conn = None
    try:
        # Read the migration file
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Connect to the database
        conn = get_db_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Execute the migration
        cursor = conn.cursor()
        cursor.execute(sql)
        
        print(f"Successfully applied {direction} migration: {migration_file}")
    except Exception as e:
        print(f"Error applying {direction} migration: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python apply_migration.py <migration_file> [up|down]")
        print("  If direction is not specified, 'up' is assumed")
        sys.exit(1)
    
    migration_file = sys.argv[1]
    direction = sys.argv[2] if len(sys.argv) == 3 else "up"
    
    if direction not in ["up", "down"]:
        print("Direction must be either 'up' or 'down'")
        sys.exit(1)
    
    apply_migration(migration_file, direction) 