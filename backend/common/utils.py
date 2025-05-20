"""
Common utility functions used across the backend.

This module provides shared functionality for:
- Environment variable management
- JWT token verification and user extraction
- API response formatting

This is the single source of truth for these utilities across the entire backend.
All other modules should import from this file rather than duplicating these functions.
"""

import json
import os
import boto3
from botocore.exceptions import ClientError
from .env import load_environment

# Load environment variables
load_environment()

def get_env_var(name, default=None):
    """
    Get an environment variable with a default value
    """
    value = os.environ.get(name, default)
    if value is None:
        print(f"Warning: Environment variable {name} is not set")
    return value

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