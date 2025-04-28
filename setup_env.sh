#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up environment variables for SwolePT...${NC}"

# Check if infrastructure/.env exists
if [ ! -f "infrastructure/.env" ]; then
    echo -e "${YELLOW}Error: infrastructure/.env file not found${NC}"
    exit 1
fi

# Create backend/.env
echo -e "${GREEN}Creating backend/.env...${NC}"
cat > backend/.env << EOL
# Database Configuration
DATABASE_URL=postgresql://${RDS_DATABASE_USER}:${RDS_DATABASE_PASSWORD}@${RDS_DATABASE_HOST}:${RDS_DATABASE_PORT}/${RDS_DATABASE_NAME}

# AWS Configuration
AWS_REGION=${AWS_REGION}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}

# S3 Configuration
S3_BUCKET_NAME=${S3_BUCKET_NAME}

# API Configuration
API_BASE_URL=https://${API_GATEWAY_ID}.execute-api.${AWS_REGION}.amazonaws.com/${API_STAGE_NAME}
EOL

# Create frontend/.env
echo -e "${GREEN}Creating frontend/.env...${NC}"
cat > frontend/.env << EOL
# API Configuration
REACT_APP_API_BASE_URL=https://${API_GATEWAY_ID}.execute-api.${AWS_REGION}.amazonaws.com/${API_STAGE_NAME}

# Cognito Configuration
REACT_APP_USER_POOL_ID=${COGNITO_USER_POOL_ID}
REACT_APP_USER_POOL_WEB_CLIENT_ID=${COGNITO_APP_CLIENT_ID}
REACT_APP_REGION=${AWS_REGION}

# S3 Configuration
REACT_APP_S3_BUCKET=${S3_BUCKET_NAME}
EOL

echo -e "${GREEN}Environment variables have been set up successfully!${NC}"
echo -e "${YELLOW}Please review the generated .env files in the backend and frontend directories.${NC}" 