from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import boto3
import openai
from .auth import register_user, login_user, require_auth
from .db import process_workout_csv, verify_db_ready, get_db_connection
import jwt
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor
import requests
import json
import time
from requests.exceptions import RequestException
import random

# Load environment variables
load_dotenv('../.env.local')

# Get JWT secret from environment variables
JWT_SECRET = os.getenv('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is not set")

# Configure OpenAI
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Validate API key format
if not (api_key.startswith('sk-') or api_key.startswith('sk-proj-')):
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
        
        # Calculate date 3 months ago
        three_months_ago = datetime.now() - timedelta(days=90)
        
        # Fetch workout history for the user from the last 3 months
        cursor.execute("""
            SELECT 
                id, date, exercise, category, 
                weight, weight_unit, reps, 
                distance, distance_unit, time, comment,
                created_at
            FROM workout_history 
            WHERE user_id = %s 
            AND date >= %s
            ORDER BY date DESC, created_at DESC
        """, (user_id, three_months_ago))
        
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

@app.route('/analyze-workouts', methods=['POST'])
@require_auth
def analyze_workouts():
    try:
        data = request.json
        workout_history = data.get('workoutHistory', [])
        
        if not workout_history:
            return jsonify({'error': 'No workout history provided'}), 400

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

        print(f"API Key found (first 10 chars): {api_key[:10]}...")
        print(f"OpenAI library version: {openai.__version__}")

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
        print("Making OpenAI API request with:")
        print(f"URL: https://api.openai.com/v1/chat/completions")
        print(f"Headers: {headers}")
        print(f"Data: {json.dumps(data, indent=2)}")

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
                print(f"Attempt {attempt + 1}/{max_retries}: Status code: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                
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
                        print(f"Rate limited. Retrying in {delay:.2f} seconds...")
                        print(f"Rate limit headers: {dict(response.headers)}")
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
                    print(f"Response text: {response.text}")
                    if "model_not_found" in response.text:
                        print("Model not found error - trying alternative model...")
                        data["model"] = "gpt-4"  # Try the standard GPT-4 model
                        continue
                
                # Check for other errors
                response.raise_for_status()
                
                # Parse the response
                result = response.json()
                analysis = result['choices'][0]['message']['content']
                
                # Log additional response details
                print(f"Model used: {result.get('model')}")
                print(f"Token usage: {result.get('usage')}")
                if result['choices'][0]['message'].get('refusal'):
                    print(f"Refusal reason: {result['choices'][0]['message']['refusal']}")
                if result['choices'][0]['message'].get('annotations'):
                    print(f"Annotations: {result['choices'][0]['message']['annotations']}")
                
                return jsonify({'analysis': analysis})

            except RequestException as e:
                print(f"Request exception on attempt {attempt + 1}: {str(e)}")
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
                    print(f"Error response status: {e.response.status_code}")
                    print(f"Error response text: {e.response.text}")
                    if e.response.status_code == 429:
                        retry_after = e.response.headers.get('Retry-After')
                        delay = int(retry_after) if retry_after else min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                        print(f"Rate limited. Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                        continue
                raise  # Re-raise if it's not a handled error

    except Exception as e:
        print(f"Error analyzing workouts: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('BACKEND_PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True) 