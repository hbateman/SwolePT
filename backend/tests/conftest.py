import os
import sys
import pytest
import json
from unittest.mock import MagicMock, patch
from ..db.providers import get_provider

# Add the parent directory to the path to import common utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock event for testing
def create_mock_event(body, headers=None):
    return {
        'body': json.dumps(body),
        'headers': headers or {}
    }

# Mock context for testing
class MockContext:
    def __init__(self):
        self.function_name = 'test-function'
        self.function_version = 'test-version'
        self.memory_limit_in_mb = 128
        self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test-function'
        self.aws_request_id = 'test-request-id'
        self.log_group_name = 'test-log-group'
        self.log_stream_name = 'test-log-stream'

    def get_remaining_time_in_millis(self):
        return 30000

# Mock user for testing
@pytest.fixture
def mock_user():
    return {
        'user_id': 'test-user-id',
        'username': 'testuser',
        'email': 'test@example.com'
    }

# Mock token for testing
@pytest.fixture
def mock_token():
    return 'mock-token'

# Mock authorization header for testing
@pytest.fixture
def mock_auth_header(mock_token):
    return {'Authorization': f'Bearer {mock_token}'}

# Mock Cognito client for testing
@pytest.fixture
def mock_cognito():
    with patch('boto3.client') as mock:
        client = MagicMock()
        mock.return_value = client
        
        # Mock successful authentication
        client.initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'mock_access_token',
                'IdToken': 'mock_id_token',
                'RefreshToken': 'mock_refresh_token'
            }
        }
        
        # Mock successful user registration
        client.sign_up.return_value = {
            'UserSub': 'mock_user_id',
            'UserConfirmed': False
        }
        
        # Mock successful confirmation
        client.confirm_sign_up.return_value = {}
        
        yield client

# Mock database provider for testing
@pytest.fixture
def mock_db():
    """Mock database provider for testing."""
    with patch('providers.get_provider') as mock:
        mock_provider = MagicMock()
        mock.return_value = mock_provider
        yield mock_provider 