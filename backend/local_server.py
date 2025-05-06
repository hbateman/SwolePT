from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import boto3
from local_auth import register_user, login_user, require_auth

# Load environment variables
load_dotenv()

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
@require_auth
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Upload to LocalStack S3
        bucket_name = os.getenv('UPLOAD_BUCKET_NAME')
        file_key = f"{request.user['sub']}/{file.filename}"
        
        s3.upload_fileobj(file, bucket_name, file_key)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'url': f"{os.getenv('AWS_ENDPOINT_URL')}/{bucket_name}/{file_key}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('BACKEND_PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True) 