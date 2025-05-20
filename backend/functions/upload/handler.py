import json
import os
import boto3
import base64
import uuid
from datetime import datetime
from ...common.utils import create_response, verify_token, get_user_from_token

# Initialize S3 client
s3_client = boto3.client('s3')

def main(event, context):
    """
    Main handler for file uploads
    """
    try:
        # Parse the incoming event
        body = json.loads(event.get('body', '{}'))
        
        # Verify authentication token
        auth_header = event.get('headers', {}).get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return create_response(401, {'error': 'Unauthorized: Missing or invalid token'})
        
        token = auth_header.split(' ')[1]
        if not verify_token(token):
            return create_response(401, {'error': 'Unauthorized: Invalid token'})
        
        # Get user information from token
        user = get_user_from_token(token)
        if not user:
            return create_response(401, {'error': 'Unauthorized: Could not extract user information'})
        
        # Get file content and name
        file_content = body.get('file_content')
        file_name = body.get('file_name')
        
        if not file_content or not file_name:
            return create_response(400, {'error': 'File content and name are required'})
        
        # Decode base64 file content
        try:
            file_data = base64.b64decode(file_content)
        except Exception as e:
            return create_response(400, {'error': 'Invalid file content encoding'})
        
        # Generate a unique file key
        file_key = f"{user['user_id']}/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}_{file_name}"
        
        # Get the S3 bucket name from environment variable
        bucket_name = os.environ.get('UPLOAD_BUCKET_NAME')
        if not bucket_name:
            return create_response(500, {'error': 'Upload bucket not configured'})
        
        # Upload file to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=file_data,
            ContentType='text/csv'
        )
        
        return create_response(200, {
            'message': 'File uploaded successfully',
            'file_key': file_key
        })
    except Exception as e:
        return create_response(500, {'error': str(e)}) 