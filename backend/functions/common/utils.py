import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import boto3
from botocore.exceptions import ClientError

def create_response(status_code, body):
    """
    Create a standardized API Gateway response
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

def get_db_connection():
    """
    Create a connection to the PostgreSQL database
    """
    try:
        # Get database connection details from environment variables
        host = os.environ.get('DATABASE_HOST')
        port = os.environ.get('DATABASE_PORT')
        database = os.environ.get('DATABASE_NAME')
        user = os.environ.get('DATABASE_USER')
        password = os.environ.get('DATABASE_PASSWORD')
        
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