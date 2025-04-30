import boto3
import os
import time
import json
import sys
from botocore.config import Config
from dotenv import load_dotenv

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
        'RDS_DATABASE_USER', 'RDS_DATABASE_PASSWORD',
        'AWS_ENDPOINT_URL', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION', 'UPLOAD_BUCKET_NAME', 'API_GATEWAY_NAME', 'API_STAGE_NAME',
        'LAMBDA_TIMEOUT', 'LAMBDA_MEMORY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Error: Missing required environment variables: {', '.join(missing_vars)}")
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
        
        print("✅ Local development environment setup complete!")
        
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 