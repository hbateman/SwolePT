import json
import os
import boto3
from botocore.exceptions import ClientError
import sys
import os

# Add the parent directory to the path to import common utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.utils import create_response, get_db_connection, execute_query

# Initialize Cognito client
cognito = boto3.client('cognito-idp')

def main(event, context):
    """
    Main handler for authentication functions
    """
    try:
        # Parse the incoming event
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        
        if action == 'login':
            return handle_login(body)
        elif action == 'register':
            return handle_register(body)
        elif action == 'confirm':
            return handle_confirm(body)
        elif action == 'refresh':
            return handle_refresh_token(body)
        else:
            return create_response(400, {'error': 'Invalid action'})
    except Exception as e:
        return create_response(500, {'error': str(e)})

def handle_login(body):
    """
    Handle user login with Cognito
    """
    try:
        username = body.get('username')
        password = body.get('password')
        
        if not username or not password:
            return create_response(400, {'error': 'Username and password are required'})
        
        # Get user pool ID and client ID from environment variables
        user_pool_id = os.environ.get('USER_POOL_ID')
        client_id = os.environ.get('USER_POOL_CLIENT_ID')
        
        # Authenticate user with Cognito
        response = cognito.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            ClientId=client_id,
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        # Return tokens
        return create_response(200, {
            'message': 'Login successful',
            'tokens': {
                'accessToken': response['AuthenticationResult']['AccessToken'],
                'idToken': response['AuthenticationResult']['IdToken'],
                'refreshToken': response['AuthenticationResult']['RefreshToken']
            }
        })
    except ClientError as e:
        if e.response['Error']['Code'] == 'NotAuthorizedException':
            return create_response(401, {'error': 'Invalid username or password'})
        elif e.response['Error']['Code'] == 'UserNotConfirmedException':
            return create_response(403, {'error': 'User is not confirmed'})
        else:
            return create_response(500, {'error': str(e)})

def handle_register(body):
    """
    Handle user registration with Cognito
    """
    try:
        username = body.get('username')
        password = body.get('password')
        email = body.get('email')
        given_name = body.get('given_name')
        family_name = body.get('family_name')
        
        if not all([username, password, email, given_name, family_name]):
            return create_response(400, {'error': 'All fields are required'})
        
        # Get user pool ID and client ID from environment variables
        user_pool_id = os.environ.get('USER_POOL_ID')
        client_id = os.environ.get('USER_POOL_CLIENT_ID')
        
        # Register user with Cognito
        response = cognito.sign_up(
            ClientId=client_id,
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'given_name', 'Value': given_name},
                {'Name': 'family_name', 'Value': family_name}
            ]
        )
        
        # Create user record in database
        try:
            query = """
            INSERT INTO users (user_id, username, email, given_name, family_name)
            VALUES (%s, %s, %s, %s, %s)
            """
            params = (
                response['UserSub'],
                username,
                email,
                given_name,
                family_name
            )
            execute_query(query, params, fetch=False)
        except Exception as db_error:
            print(f"Error creating user in database: {str(db_error)}")
            # Continue even if database insert fails, as the user is still created in Cognito
        
        return create_response(200, {
            'message': 'Registration successful',
            'userSub': response['UserSub'],
            'userConfirmed': response['UserConfirmed']
        })
    except ClientError as e:
        if e.response['Error']['Code'] == 'UsernameExistsException':
            return create_response(400, {'error': 'Username already exists'})
        else:
            return create_response(500, {'error': str(e)})

def handle_confirm(body):
    """
    Handle user confirmation with Cognito
    """
    try:
        username = body.get('username')
        code = body.get('code')
        
        if not username or not code:
            return create_response(400, {'error': 'Username and confirmation code are required'})
        
        # Get client ID from environment variables
        client_id = os.environ.get('USER_POOL_CLIENT_ID')
        
        # Confirm user with Cognito
        cognito.confirm_sign_up(
            ClientId=client_id,
            Username=username,
            ConfirmationCode=code
        )
        
        return create_response(200, {'message': 'User confirmed successfully'})
    except ClientError as e:
        if e.response['Error']['Code'] == 'CodeMismatchException':
            return create_response(400, {'error': 'Invalid confirmation code'})
        elif e.response['Error']['Code'] == 'ExpiredCodeException':
            return create_response(400, {'error': 'Confirmation code has expired'})
        else:
            return create_response(500, {'error': str(e)})

def handle_refresh_token(body):
    """
    Handle refreshing access token with refresh token
    """
    try:
        refresh_token = body.get('refreshToken')
        
        if not refresh_token:
            return create_response(400, {'error': 'Refresh token is required'})
        
        # Get client ID from environment variables
        client_id = os.environ.get('USER_POOL_CLIENT_ID')
        
        # Refresh token with Cognito
        response = cognito.initiate_auth(
            AuthFlow='REFRESH_TOKEN_AUTH',
            ClientId=client_id,
            AuthParameters={
                'REFRESH_TOKEN': refresh_token
            }
        )
        
        return create_response(200, {
            'message': 'Token refreshed successfully',
            'tokens': {
                'accessToken': response['AuthenticationResult']['AccessToken'],
                'idToken': response['AuthenticationResult']['IdToken']
            }
        })
    except ClientError as e:
        if e.response['Error']['Code'] == 'NotAuthorizedException':
            return create_response(401, {'error': 'Invalid refresh token'})
        else:
            return create_response(500, {'error': str(e)}) 