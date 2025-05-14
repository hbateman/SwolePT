import jwt
import os
import datetime
from functools import wraps
from flask import request, jsonify
from local_db import create_user, get_user, verify_password, get_db_connection
import uuid
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash

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
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
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
        # Generate a UUID-like user_id to match Cognito's format
        user_id = str(uuid.uuid4())
        username = email  # Use email as username, matching Cognito's default behavior
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Create user in database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Insert new user
        cursor.execute("""
            INSERT INTO users (user_id, username, email, password_hash, given_name, family_name)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING user_id
        """, (user_id, username, email, password_hash, given_name or email.split('@')[0], family_name or ''))
        
        result = cursor.fetchone()
        conn.commit()
        
        # Generate token
        token = generate_token(result['user_id'], email)
        
        return {
            'token': token,
            'user': {
                'user_id': result['user_id'],
                'email': email,
                'username': username,
                'given_name': given_name,
                'family_name': family_name
            }
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 400
    finally:
        if conn:
            conn.close()

def login_user(email, password):
    """Login a user locally."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get user
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            return {'error': 'Invalid credentials'}, 401
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return {'error': 'Invalid credentials'}, 401
        
        # Generate token
        token = generate_token(user['user_id'], email)
        
        return {
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'email': user['email'],
                'username': user['username'],
                'given_name': user['given_name'],
                'family_name': user['family_name']
            }
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 400
    finally:
        if conn:
            conn.close() 