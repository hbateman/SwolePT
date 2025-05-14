import boto3
import os
import time
import json
import sys
import subprocess
import psycopg2
from botocore.config import Config
from dotenv import load_dotenv
from sqlalchemy import inspect
from database import engine, Base
from models import User, WorkoutHistory

def check_docker_container(container_name):
    """Check if a Docker container is running and healthy."""
    try:
        # Get detailed container information
        result = subprocess.run(
            ['docker', 'ps', '-a', '--filter', f'name={container_name}', '--format', '{{.Names}}|{{.Status}}|{{.State}}'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if not result.stdout.strip():
            print(f"❌ Container {container_name} not found")
            return False
            
        # Parse container information
        container_info = result.stdout.strip().split('|')
        print(f"Container status: {container_info[1]}")
        print(f"Container state: {container_info[2]}")
        
        # Check if container is running
        if 'Up' not in container_info[1]:
            print(f"❌ Container {container_name} is not running")
            return False
            
        # Check if container is healthy
        if 'healthy' not in container_info[1]:
            print(f"❌ Container {container_name} is not healthy")
            return False
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking container status: {str(e)}")
        return False

def wait_for_postgres():
    """Wait for PostgreSQL to be ready."""
    max_attempts = 30
    attempt = 1
    
    print("Waiting for PostgreSQL container to be ready...")
    
    # First, check if the container is running and healthy
    while attempt <= max_attempts:
        print(f"\nChecking container status (attempt {attempt}/{max_attempts})...")
        if check_docker_container('swolept-postgres'):
            print("✅ PostgreSQL container is healthy!")
            break
        print(f"Waiting for PostgreSQL container (attempt {attempt}/{max_attempts})...")
        time.sleep(2)
        attempt += 1
    else:
        print("❌ PostgreSQL container failed to become healthy")
        return False
    
    # Now try to connect to the database
    attempt = 1
    print("\nAttempting to connect to PostgreSQL...")
    
    # Get connection details from environment
    host = os.getenv('DATABASE_HOST')
    port = os.getenv('DATABASE_PORT')
    user = os.getenv('RDS_DATABASE_USER')
    password = os.getenv('RDS_DATABASE_PASSWORD')
    database = os.getenv('RDS_DATABASE_NAME')
    
    # Print connection details (without password)
    print(f"Connection details:")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  User: {user}")
    print(f"  Database: {database}")
    
    while attempt <= max_attempts:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            conn.close()
            print("✅ Successfully connected to PostgreSQL!")
            return True
        except psycopg2.OperationalError as e:
            print(f"❌ Connection error: {str(e)}")
            print(f"Waiting for PostgreSQL connection (attempt {attempt}/{max_attempts})...")
            time.sleep(2)
            attempt += 1
    
    print("❌ Failed to connect to PostgreSQL")
    return False

def load_environment():
    """Load environment variables from .env file."""
    # Get the project root directory (two levels up from this script)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, '.env')
    
    if not os.path.exists(env_path):
        print(f"❌ Error: .env file not found at {env_path}")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    # Validate required environment variables
    required_vars = [
        'DATABASE_HOST', 'DATABASE_PORT', 'RDS_DATABASE_NAME',
        'RDS_DATABASE_USER', 'RDS_DATABASE_PASSWORD',  # Required for Docker setup
        'AWS_ENDPOINT_URL', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION', 'UPLOAD_BUCKET_NAME', 'API_GATEWAY_NAME', 'API_STAGE_NAME',
        'LAMBDA_TIMEOUT', 'LAMBDA_MEMORY', 'OPENAI_API_KEY'  # Added OpenAI API key
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
        sys.exit(1)
    
    # Validate OpenAI API key format
    api_key = os.getenv('OPENAI_API_KEY')
    if not (api_key.startswith('sk-') or api_key.startswith('sk-proj-')):
        print("❌ Error: Invalid OpenAI API key format. Key must start with 'sk-' or 'sk-proj-'")
        sys.exit(1)

def get_localstack_client(service):
    """Create a boto3 client for LocalStack."""
    return boto3.client(
        service,
        endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION'),
        config=Config(
            retries=dict(
                max_attempts=10
            )
        )
    )

def setup_s3():
    """Set up S3 bucket in LocalStack."""
    s3 = get_localstack_client('s3')
    bucket_name = os.getenv('UPLOAD_BUCKET_NAME')
    
    try:
        s3.create_bucket(Bucket=bucket_name)
        print(f"✅ Created S3 bucket: {bucket_name}")
    except s3.exceptions.BucketAlreadyExists:
        print(f"ℹ️ S3 bucket already exists: {bucket_name}")
    except Exception as e:
        print(f"❌ Error creating S3 bucket: {str(e)}")
        sys.exit(1)

def check_database_tables():
    """Check if required database tables exist."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    required_tables = ['users', 'workout_history']
    return all(table in existing_tables for table in required_tables)

def setup_database():
    """Set up database tables and migrations."""
    try:
        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create tables
        print("Creating database tables...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id VARCHAR(255) PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                given_name VARCHAR(255),
                family_name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) REFERENCES users(user_id),
                date TIMESTAMP NOT NULL,
                type VARCHAR(50) NOT NULL,
                duration INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Database tables created successfully")
        
        # Apply migrations using the CLI tool
        print("Applying migrations...")
        from db.management.cli import run_migrations
        run_migrations()
        print("✅ Migrations applied successfully")
        
    except Exception as e:
        print(f"❌ Error setting up database: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def wait_for_services():
    """Wait for LocalStack services to be ready."""
    print("Waiting for LocalStack services to be ready...")
    time.sleep(5)  # Give services time to initialize

def main():
    """Main setup function."""
    try:
        # Load and validate environment
        load_environment()
        
        # Wait for services
        wait_for_services()
        
        # Set up services
        setup_s3()
        setup_database()
        
        print("✅ Local development environment setup complete!")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 