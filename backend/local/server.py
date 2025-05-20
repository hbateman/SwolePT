print("[server.py] Starting server.py execution...")
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from pathlib import Path
from datetime import datetime, timedelta
import jwt
from db.providers import get_provider
from db.setup import setup_database
from common.env import load_environment
import boto3
import openai
from .auth import register_user, login_user, require_auth
import requests
import json
import time
from requests.exceptions import RequestException
import random
import csv
from io import StringIO

# Ensure log directory exists and is writable
base_dir = Path(__file__).resolve().parent
log_dir = base_dir / 'logs'
log_dir.mkdir(exist_ok=True, parents=True)
log_file = log_dir / 'backend.log'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(str(log_file), mode='a'),  # Use append mode
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("="*50)
logger.info("Starting server...")
logger.info(f"Log file: {log_file}")

# Load environment variables
load_environment()

# Get JWT secret from environment variables
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    logger.error("JWT_SECRET environment variable is not set")
    raise ValueError("JWT_SECRET environment variable is not set")

# Configure OpenAI
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Validate API key format
if not (api_key.startswith('sk-') or api_key.startswith('sk-proj-')):
    logger.error("Invalid OpenAI API key format. Key must start with 'sk-' or 'sk-proj-'")
    raise ValueError("Invalid OpenAI API key format. Key must start with 'sk-' or 'sk-proj-'")

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

def verify_db_ready():
    """Verify that the database is ready and initialized."""
    try:
        # Initialize database
        setup_database()
        
        # Test connection
        db = get_provider()
        db.connect()
        
        logger.info("✅ Database is ready!")
        return True
    except Exception as e:
        logger.error(f"❌ Database not ready: {str(e)}")
        raise e

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
    name = data.get('name')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Split name into given_name and family_name
    name_parts = name.split(' ') if name else []
    given_name = name_parts[0] if name_parts else email.split('@')[0]
    family_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
    return register_user(email, password, given_name, family_name)

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
            logger.info(f"Processing upload for user {user_id}")
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        # Check if file was uploaded
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400

        logger.info(f"Processing file: {file.filename}")
        
        # Read the CSV content
        csv_content = file.read().decode('utf-8')
        logger.info(f"Read {len(csv_content)} bytes from CSV file")
        
        # Process the CSV using the provider
        db = get_provider()
        logger.info("Processing CSV content...")
        processed_records = db.process_workout_csv(user_id, csv_content)
        logger.info(f"Successfully processed {len(processed_records)} records")
        
        return jsonify({
            'message': 'File processed successfully',
            'records_processed': len(processed_records),
            'records': processed_records
        })

    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/workout-history', methods=['GET'])
@require_auth
def get_workout_history():
    try:
        user_id = request.user['sub']
        db = get_provider()
        
        # Calculate date 3 months ago
        three_months_ago = datetime.now() - timedelta(days=90)
        
        # Fetch workout history using the provider
        workouts = db.get_workout_records(user_id, start_date=three_months_ago)
        logger.info(f"Found {len(workouts)} workout records for user {user_id}")
        
        # Convert to list of dictionaries for JSON serialization
        workout_list = []
        for workout in workouts:
            workout_dict = {
                'id': workout.id,
                'date': workout.date.isoformat(),
                'exercise': workout.exercise,
                'category': workout.category,
                'weight': workout.weight,
                'weight_unit': workout.weight_unit,
                'reps': workout.reps,
                'distance': workout.distance,
                'distance_unit': workout.distance_unit,
                'time': workout.time,
                'comment': workout.comment,
                'created_at': workout.created_at.isoformat()
            }
            workout_list.append(workout_dict)
        
        logger.info(f"Returning {len(workout_list)} workout records")
        return jsonify(workout_list)
        
    except Exception as e:
        logger.error(f"Error getting workout history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/analyze-workouts', methods=['POST'])
@require_auth
def analyze_workouts():
    try:
        data = request.json
        logger.info(f"Received request data: {json.dumps(data, indent=2)}")
        
        if not data:
            logger.error("No data received in request")
            return jsonify({'error': 'No data provided'}), 400
            
        workout_history = data.get('workoutHistory')
        logger.info(f"Extracted workout history: {json.dumps(workout_history, indent=2)}")
        
        if not workout_history:
            logger.error("No workout history found in request data")
            return jsonify({'error': 'No workout history provided'}), 400
            
        if not isinstance(workout_history, list):
            logger.error(f"Workout history is not a list: {type(workout_history)}")
            return jsonify({'error': 'Workout history must be a list'}), 400
            
        if len(workout_history) == 0:
            logger.error("Workout history list is empty")
            return jsonify({'error': 'No workout history found. Please upload some workout data first.'}), 400

        # Format workout history for the prompt
        workout_summary = "\n".join([
            "Date: {}, Exercise: {}, Category: {}, {}{}{}{}{}".format(
                workout['date'],
                workout['exercise'],
                workout['category'],
                f"Weight: {workout['weight']} {workout['weight_unit']}, " if workout.get('weight') else "",
                f"Reps: {workout['reps']}, " if workout.get('reps') else "",
                f"Distance: {workout['distance']} {workout['distance_unit']}, " if workout.get('distance') else "",
                f"Time: {workout['time']}, " if workout.get('time') else "",
                f"Comment: {workout['comment']}" if workout.get('comment') else ""
            )
            for workout in workout_history
        ])

        # Create the prompt for OpenAI
        prompt = f"""Based on the following workout history, provide a detailed analysis of the user's fitness journey, 
        including patterns, progress, and recommendations. Focus on:
        1. Exercise frequency and consistency
        2. Progress in weights/reps/distance
        3. Exercise variety
        4. Potential areas for improvement
        5. Specific recommendations for future workouts

        Workout History:
        {workout_summary}

        Please provide a comprehensive analysis:"""

        logger.info(f"API Key found (first 10 chars): {api_key[:10]}...")
        logger.info(f"OpenAI library version: {openai.__version__}")

        # Prepare the request
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-4-turbo-2024-04-09",  # Updated to the latest GPT-4 model
            "messages": [
                {"role": "system", "content": "You are a knowledgeable fitness trainer and analyst."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

        # Print request details for debugging
        logger.info("Making OpenAI API request with:")
        logger.info(f"URL: https://api.openai.com/v1/chat/completions")
        logger.info(f"Headers: {headers}")
        logger.info(f"Data: {json.dumps(data, indent=2)}")

        # Retry logic with exponential backoff
        max_retries = 5  # Increased from 3 to 5
        base_delay = 10  # Increased from 1 to 2 seconds
        max_delay = 60  # Maximum delay of 32 seconds
        
        for attempt in range(max_retries):
            try:
                # Make the API call
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                # Print response details for debugging
                logger.info(f"Attempt {attempt + 1}/{max_retries}: Status code: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                # Handle rate limiting
                if response.status_code == 429:
                    # Get rate limit info from headers
                    retry_after = response.headers.get('Retry-After')
                    if retry_after:
                        delay = int(retry_after)
                    else:
                        # Calculate exponential backoff with jitter
                        delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                    
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        logger.info(f"Rate limited. Retrying in {delay:.2f} seconds...")
                        logger.info(f"Rate limit headers: {dict(response.headers)}")
                        time.sleep(delay)
                        continue
                    else:
                        return jsonify({
                            'error': 'OpenAI API rate limit exceeded. Please try again in a few minutes.',
                            'details': {
                                'status_code': 429,
                                'headers': dict(response.headers),
                                'attempts': attempt + 1
                            }
                        }), 429
                
                if response.status_code != 200:
                    logger.info(f"Response text: {response.text}")
                    if "model_not_found" in response.text:
                        logger.info("Model not found error - trying alternative model...")
                        data["model"] = "gpt-4"  # Try the standard GPT-4 model
                        continue
                
                # Check for other errors
                response.raise_for_status()
                
                # Parse the response
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                
                # Log additional response details
                logger.info(f"Model used: {result.get('model')}")
                logger.info(f"Token usage: {result.get('usage')}")
                if result['choices'][0]['message'].get('refusal'):
                    logger.info(f"Refusal reason: {result['choices'][0]['message']['refusal']}")
                if result['choices'][0]['message'].get('annotations'):
                    logger.info(f"Annotations: {result['choices'][0]['message']['annotations']}")
                
                return jsonify({'analysis': analysis})

            except RequestException as e:
                logger.info(f"Request exception on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    error_details = {
                        'error': str(e),
                        'attempts': attempt + 1,
                        'max_retries': max_retries
                    }
                    if hasattr(e, 'response') and e.response is not None:
                        error_details['status_code'] = e.response.status_code
                        error_details['headers'] = dict(e.response.headers)
                        error_details['response_text'] = e.response.text
                    return jsonify({'error': f"OpenAI API error: {str(e)}", 'details': error_details}), 500
                
                if hasattr(e, 'response') and e.response is not None:
                    logger.info(f"Error response status: {e.response.status_code}")
                    logger.info(f"Error response text: {e.response.text}")
                    if e.response.status_code == 429:
                        retry_after = e.response.headers.get('Retry-After')
                        delay = int(retry_after) if retry_after else min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                        logger.info(f"Rate limited. Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                        continue
                raise  # Re-raise if it's not a handled error

    except Exception as e:
        logger.error(f"Error analyzing workouts: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('BACKEND_PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True) 