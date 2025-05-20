import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from db.providers import get_provider
from functools import wraps
from flask import request, jsonify, current_app
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get JWT secret from environment variables
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is not set")

def generate_token(user_id, email):
    """Generate a JWT token for local development.
    Uses 'sub' claim to match JWT standard and production environment (AWS Cognito).
    """
    payload = {
        'sub': user_id,  # Using 'sub' to match JWT standard and production
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify a JWT token for local development."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            if not payload:
                return jsonify({'error': 'Invalid token'}), 401
            
            # Add user info to request
            request.user = payload
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated

def register_user(email, password, given_name=None, family_name=None):
    """Register a new user locally."""
    try:
        if not email or not password:
            logger.error("Missing required fields in register_user")
            return {'error': 'Email and password are required'}, 400
            
        db = get_provider()
        logger.info(f"Checking for existing user with email: {email}")
        
        # Check if user already exists
        existing_user = db.get_user_by_email(email)
        if existing_user:
            logger.error(f"User already exists with email: {email}")
            return {'error': 'User with this email already exists'}, 400
        
        # Create user in database
        try:
            logger.info(f"Creating new user: email={email}, given_name={given_name}, family_name={family_name}")
            user = db.create_user(
                username=email,  # Use email as username, matching Cognito's default behavior
                email=email,
                password_hash=generate_password_hash(password),
                given_name=given_name or email.split('@')[0],
                family_name=family_name or ''
            )
            logger.info(f"User created successfully with ID: {user.user_id}")
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            return {'error': f'Failed to create user: {str(e)}'}, 400
        
        # Generate token
        try:
            logger.info("Generating token for new user")
            token = generate_token(user.user_id, email)
            logger.info("Token generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate token: {str(e)}")
            return {'error': f'Failed to generate token: {str(e)}'}, 500
        
        return {
            'token': token,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'username': user.username,
                'given_name': user.given_name,
                'family_name': user.family_name
            }
        }, 200
        
    except Exception as e:
        logger.error(f"Registration failed with error: {str(e)}")
        return {'error': f'Registration failed: {str(e)}'}, 400

def login_user(email, password):
    """Login a user locally."""
    try:
        db = get_provider()
        
        # Get user
        user = db.get_user_by_email(email)
        if not user:
            return {'error': 'Invalid credentials'}, 401
        
        # Verify password
        if not db.verify_password(password, user.password_hash):
            return {'error': 'Invalid credentials'}, 401
        
        # Generate token
        token = generate_token(user.user_id, email)
        
        return {
            'token': token,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'username': user.username,
                'given_name': user.given_name,
                'family_name': user.family_name
            }
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 400 