#!/bin/bash

# Script to set up environment variables for local development

# Set default values
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${DB_NAME:-"swolept"}
DB_USER=${DB_USER:-"postgres"}
DB_PASSWORD=${DB_PASSWORD:-"postgres"}
USER_POOL_ID=${USER_POOL_ID:-""}
USER_POOL_CLIENT_ID=${USER_POOL_CLIENT_ID:-""}
UPLOAD_BUCKET_NAME=${UPLOAD_BUCKET_NAME:-""}
AWS_REGION=${AWS_REGION:-"us-east-1"}
API_BASE_URL=${API_BASE_URL:-"http://localhost:3000"}
FRONTEND_URL=${FRONTEND_URL:-"http://localhost:3000"}
DEBUG=${DEBUG:-"true"}

# Function to display usage
function show_usage {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  --host <host>              Database host (default: localhost)"
    echo "  --port <port>              Database port (default: 5432)"
    echo "  --name <name>              Database name (default: swolept)"
    echo "  --user <user>              Database user (default: postgres)"
    echo "  --password <password>      Database password (default: postgres)"
    echo "  --user-pool-id <id>        Cognito User Pool ID"
    echo "  --user-pool-client-id <id> Cognito User Pool Client ID"
    echo "  --bucket-name <name>       S3 Bucket name for uploads"
    echo "  --region <region>          AWS Region (default: us-east-1)"
    echo "  --api-url <url>            API Base URL (default: http://localhost:3000)"
    echo "  --frontend-url <url>       Frontend URL (default: http://localhost:3000)"
    echo "  --debug <true|false>       Debug mode (default: true)"
    echo "  --use-example              Use .env.example as a template"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_usage
            exit 0
            ;;
        --host)
            DB_HOST="$2"
            shift 2
            ;;
        --port)
            DB_PORT="$2"
            shift 2
            ;;
        --name)
            DB_NAME="$2"
            shift 2
            ;;
        --user)
            DB_USER="$2"
            shift 2
            ;;
        --password)
            DB_PASSWORD="$2"
            shift 2
            ;;
        --user-pool-id)
            USER_POOL_ID="$2"
            shift 2
            ;;
        --user-pool-client-id)
            USER_POOL_CLIENT_ID="$2"
            shift 2
            ;;
        --bucket-name)
            UPLOAD_BUCKET_NAME="$2"
            shift 2
            ;;
        --region)
            AWS_REGION="$2"
            shift 2
            ;;
        --api-url)
            API_BASE_URL="$2"
            shift 2
            ;;
        --frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        --debug)
            DEBUG="$2"
            shift 2
            ;;
        --use-example)
            USE_EXAMPLE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if .env.example exists and --use-example flag is set
if [[ "$USE_EXAMPLE" == "true" && -f ".env.example" ]]; then
    echo "Using .env.example as a template..."
    cp .env.example .env
    
    # Replace placeholder values with provided values
    sed -i.bak "s/DATABASE_HOST=.*/DATABASE_HOST=$DB_HOST/" .env
    sed -i.bak "s/DATABASE_PORT=.*/DATABASE_PORT=$DB_PORT/" .env
    sed -i.bak "s/DATABASE_NAME=.*/DATABASE_NAME=$DB_NAME/" .env
    sed -i.bak "s/DATABASE_USER=.*/DATABASE_USER=$DB_USER/" .env
    sed -i.bak "s/DATABASE_PASSWORD=.*/DATABASE_PASSWORD=$DB_PASSWORD/" .env
    
    if [[ -n "$USER_POOL_ID" ]]; then
        sed -i.bak "s/USER_POOL_ID=.*/USER_POOL_ID=$USER_POOL_ID/" .env
    fi
    
    if [[ -n "$USER_POOL_CLIENT_ID" ]]; then
        sed -i.bak "s/USER_POOL_CLIENT_ID=.*/USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID/" .env
    fi
    
    if [[ -n "$UPLOAD_BUCKET_NAME" ]]; then
        sed -i.bak "s/UPLOAD_BUCKET_NAME=.*/UPLOAD_BUCKET_NAME=$UPLOAD_BUCKET_NAME/" .env
    fi
    
    sed -i.bak "s/AWS_REGION=.*/AWS_REGION=$AWS_REGION/" .env
    sed -i.bak "s/API_BASE_URL=.*/API_BASE_URL=$API_BASE_URL/" .env
    sed -i.bak "s/FRONTEND_URL=.*/FRONTEND_URL=$FRONTEND_URL/" .env
    sed -i.bak "s/DEBUG=.*/DEBUG=$DEBUG/" .env
    
    # Clean up backup files
    rm -f .env.bak
    
    echo "Created .env file from .env.example template with your values."
else
    # Create .env file from scratch
    cat > .env << EOF
# Database configuration
DATABASE_HOST=$DB_HOST
DATABASE_PORT=$DB_PORT
DATABASE_NAME=$DB_NAME
DATABASE_USER=$DB_USER
DATABASE_PASSWORD=$DB_PASSWORD

# Cognito configuration
USER_POOL_ID=$USER_POOL_ID
USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID

# S3 configuration
UPLOAD_BUCKET_NAME=$UPLOAD_BUCKET_NAME

# AWS Region
AWS_REGION=$AWS_REGION

# API Configuration
API_BASE_URL=$API_BASE_URL

# Frontend Configuration
FRONTEND_URL=$FRONTEND_URL

# Development Mode
DEBUG=$DEBUG
EOF

    echo "Created .env file with the following values:"
fi

echo ""
echo "Environment variables set up in .env file:"
echo "  DATABASE_HOST=$DB_HOST"
echo "  DATABASE_PORT=$DB_PORT"
echo "  DATABASE_NAME=$DB_NAME"
echo "  DATABASE_USER=$DB_USER"
echo "  DATABASE_PASSWORD=$DB_PASSWORD"
echo "  USER_POOL_ID=$USER_POOL_ID"
echo "  USER_POOL_CLIENT_ID=$USER_POOL_CLIENT_ID"
echo "  UPLOAD_BUCKET_NAME=$UPLOAD_BUCKET_NAME"
echo "  AWS_REGION=$AWS_REGION"
echo "  API_BASE_URL=$API_BASE_URL"
echo "  FRONTEND_URL=$FRONTEND_URL"
echo "  DEBUG=$DEBUG"
echo ""
echo "To use these variables in your shell, run:"
echo "  source .env"
echo ""
echo "To use these variables with Python, install python-dotenv and load the .env file in your code." 