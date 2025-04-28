import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import the auth handler
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions.auth.handler import main

@pytest.mark.auth
@pytest.mark.cognito
def test_handle_login_success(mock_cognito, mock_db_connection):
    # Setup
    event = {
        'body': json.dumps({
            'action': 'login',
            'username': 'testuser',
            'password': 'testpass'
        })
    }
    mock_cognito.initiate_auth.return_value = {
        'AuthenticationResult': {
            'AccessToken': 'mock_access_token',
            'IdToken': 'mock_id_token',
            'RefreshToken': 'mock_refresh_token'
        }
    }

    # Execute
    response = main(event, None)

    # Verify
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'message' in body
    assert body['message'] == 'Login successful'
    assert 'tokens' in body
    assert body['tokens']['accessToken'] == 'mock_access_token'
    assert body['tokens']['idToken'] == 'mock_id_token'
    assert body['tokens']['refreshToken'] == 'mock_refresh_token'
    mock_cognito.initiate_auth.assert_called_once()

@pytest.mark.auth
@pytest.mark.cognito
def test_handle_register_success(mock_cognito, mock_db_connection):
    # Setup
    event = {
        'body': json.dumps({
            'action': 'register',
            'username': 'newuser',
            'password': 'newpass',
            'email': 'newuser@example.com',
            'given_name': 'New',
            'family_name': 'User'
        })
    }
    mock_cognito.sign_up.return_value = {
        'UserConfirmed': False,
        'UserSub': 'mock-user-sub'
    }

    # Execute
    response = main(event, None)

    # Verify
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Registration successful'
    assert body['userSub'] == 'mock-user-sub'
    assert not body['userConfirmed']
    mock_cognito.sign_up.assert_called_once()

@pytest.mark.auth
def test_handle_confirm_success(mock_cognito):
    # Setup
    event = {
        'body': json.dumps({
            'action': 'confirm',
            'username': 'testuser',
            'code': '123456'
        })
    }
    mock_cognito.confirm_sign_up.return_value = {}

    # Execute
    response = main(event, None)

    # Verify
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'User confirmed successfully'
    mock_cognito.confirm_sign_up.assert_called_once()

@pytest.mark.auth
@pytest.mark.cognito
def test_handle_refresh_token_success(mock_cognito):
    # Setup
    event = {
        'body': json.dumps({
            'action': 'refresh',
            'refreshToken': 'mock_refresh_token'
        })
    }
    mock_cognito.initiate_auth.return_value = {
        'AuthenticationResult': {
            'AccessToken': 'new_access_token',
            'IdToken': 'new_id_token'
        }
    }

    # Execute
    response = main(event, None)

    # Verify
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['message'] == 'Token refreshed successfully'
    assert 'tokens' in body
    assert body['tokens']['accessToken'] == 'new_access_token'
    assert body['tokens']['idToken'] == 'new_id_token'
    mock_cognito.initiate_auth.assert_called_once()

@pytest.mark.auth
def test_invalid_action():
    # Setup
    event = {
        'body': json.dumps({
            'action': 'invalid_action'
        })
    }

    # Execute
    response = main(event, None)

    # Verify
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'Invalid action' in body['error']

@pytest.mark.auth
@pytest.mark.cognito
def test_handle_login_invalid_credentials(mock_cognito):
    # Setup
    event = {
        'body': json.dumps({
            'action': 'login',
            'username': 'testuser',
            'password': 'wrongpass'
        })
    }
    error = MagicMock()
    error.response = {'Error': {'Code': 'NotAuthorizedException'}}
    mock_cognito.initiate_auth.side_effect = error

    # Execute
    response = main(event, None)

    # Verify
    assert response['statusCode'] == 401
    body = json.loads(response['body'])
    assert 'error' in body
    assert 'Invalid username or password' in body['error'] 