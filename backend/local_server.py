from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import boto3
from local_auth import register_user, login_user, require_auth
from local_db import process_workout_csv, verify_db_ready, get_db_connection
import jwt
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv('.env.local')

# Get JWT secret from environment variables
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is not set")

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Verify database is ready before starting
verify_db_ready()

# Configure LocalStack S3 client
s3 = boto3.client(
    's3',
    endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    return register_user(email, password)

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    return login_user(email, password)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Get the authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization header'}), 401

        # Extract and verify the token
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = payload['sub']  # Using 'sub' to match JWT standard and production
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        # Read the CSV content
        csv_content = file.read().decode('utf-8')
        
        # Process the CSV and store in database
        processed_records = process_workout_csv(user_id, csv_content)
        
        return jsonify({
            'message': 'File processed successfully',
            'records_processed': len(processed_records),
            'records': processed_records
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/workout-history', methods=['GET'])
@require_auth
def get_workout_history():
    conn = None
    try:
        user_id = request.user['sub']
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Fetch workout history for the user
        cursor.execute("""
            SELECT 
                id, date, exercise, category, 
                weight, weight_unit, reps, 
                distance, distance_unit, time, comment,
                created_at
            FROM workout_history 
            WHERE user_id = %s 
            ORDER BY date DESC, created_at DESC
        """, (user_id,))
        
        workouts = cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for workout in workouts:
            workout['date'] = workout['date'].isoformat()
            workout['created_at'] = workout['created_at'].isoformat()
        
        return jsonify(workouts)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    port = int(os.getenv('BACKEND_PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True) 