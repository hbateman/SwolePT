import jwt
import os
import datetime
from functools import wraps
from flask import request, jsonify
from local_db import init_db, create_user, get_user, verify_password

# Initialize the database
init_db()

def generate_token(user_id, email):
    """Generate a JWT token for local development."""
    secret = os.getenv('JWT_SECRET', 'local-development-secret')
    payload = {
        'sub': user_id,
        'email': email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, secret, algorithm='HS256')

def verify_token(token):
    """Verify a JWT token for local development."""
    try:
        secret = os.getenv('JWT_SECRET', 'local-development-secret')
        payload = jwt.decode(token, secret, algorithms=['HS256'])
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

def register_user(email, password):
    """Register a new user locally."""
    user_id, error = create_user(email, password)
    if error:
        return {'error': error}, 400
    
    token = generate_token(user_id, email)
    return {
        'token': token,
        'user': {
            'id': user_id,
            'email': email
        }
    }, 200

def login_user(email, password):
    """Login a user locally."""
    user = get_user(email)
    if not user or not verify_password(user, password):
        return {'error': 'Invalid credentials'}, 401
    
    token = generate_token(user['id'], email)
    return {
        'token': token,
        'user': {
            'id': user['id'],
            'email': email
        }
    }, 200 