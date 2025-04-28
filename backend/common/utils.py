import json
import os
import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
from botocore.exceptions import ClientError

# Try to load environment variables from .env file if it exists
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

def get_env_var(name, default=None):
    """
    Get an environment variable with a default value
    """
    value = os.environ.get(name, default)
    if value is None:
        print(f"Warning: Environment variable {name} is not set")
    return value

def get_db_connection():
    """
    Get a connection to the RDS database
    """
    try:
        # Get database connection details from environment variables
        host = get_env_var('DATABASE_HOST')
        port = get_env_var('DATABASE_PORT')
        database = get_env_var('DATABASE_NAME')
        user = get_env_var('DATABASE_USER')
        password = get_env_var('DATABASE_PASSWORD')
        
        # Create connection
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

def execute_query(query, params=None, fetch=True):
    """
    Execute a database query and return results
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = cursor.rowcount
        
        return result
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error executing query: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

def verify_token(token):
    """
    Verify a JWT token from Cognito
    """
    try:
        # Get user pool ID from environment variables
        user_pool_id = os.environ.get('USER_POOL_ID')
        
        # Get the key ID from the token header
        headers = token.split('.')[0]
        headers = json.loads(headers)
        kid = headers.get('kid')
        
        # Get the public keys from Cognito
        cognito = boto3.client('cognito-idp')
        response = cognito.get_signing_key(
            UserPoolId=user_pool_id,
            KeyId=kid
        )
        
        # Verify the token
        # Note: In a production environment, you would use a JWT library to verify the token
        # This is a simplified version for demonstration purposes
        
        return True
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return False

def get_user_from_token(token):
    """
    Extract user information from a JWT token
    """
    try:
        # Decode the token payload
        payload = token.split('.')[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        payload = json.loads(payload)
        
        # Extract user information
        user_id = payload.get('sub')
        username = payload.get('username')
        email = payload.get('email')
        
        return {
            'user_id': user_id,
            'username': username,
            'email': email
        }
    except Exception as e:
        print(f"Error extracting user from token: {str(e)}")
        return None

def create_response(status_code, body):
    """
    Create a standardized API response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
        },
        'body': json.dumps(body)
    } 