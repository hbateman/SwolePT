# Environment Variables Setup

This document provides instructions on how to set up and use environment variables for the SwolePT application.

## Required Environment Variables

### Database Connection
- `DATABASE_HOST`: The hostname of the RDS database
- `DATABASE_PORT`: The port number of the RDS database (default: 5432)
- `DATABASE_NAME`: The name of the database
- `DATABASE_USER`: The username for the database
- `DATABASE_PASSWORD`: The password for the database

### Authentication
- `USER_POOL_ID`: The ID of the Cognito User Pool
- `USER_POOL_CLIENT_ID`: The Client ID of the Cognito User Pool

### S3 Bucket
- `UPLOAD_BUCKET_NAME`: The name of the S3 bucket for file uploads

### AWS Region
- `AWS_REGION`: The AWS region where the application is deployed (default: us-east-1)

### API Configuration
- `API_BASE_URL`: The base URL of the API (default: http://localhost:3000)

### Frontend Configuration
- `FRONTEND_URL`: The URL of the frontend application (default: http://localhost:3000)

### Development Mode
- `DEBUG`: Set to 'true' to enable debug mode (default: false)

## Local Development

### Using the Setup Script

The `setup_env.sh` script can be used to set up environment variables for local development. It can create a `.env` file from scratch or use the `.env.example` file as a template.

#### Creating a `.env` file from scratch

```bash
./setup_env.sh
```

This will create a `.env` file with default values for all required environment variables.

#### Creating a `.env` file from `.env.example`

```bash
./setup_env.sh --use-example
```

This will copy the `.env.example` file to `.env` and replace any placeholder values with the values provided in the command line arguments.

#### Customizing Environment Variables

You can customize the environment variables by passing them as command line arguments:

```bash
./setup_env.sh --db-host=my-db-host --db-port=5432 --db-name=my-db --db-user=my-user --db-password=my-password
```

### Using the `.env` file

To use the environment variables in your shell:

```bash
source .env
```

To use the environment variables in your Python code, install the `python-dotenv` package:

```bash
pip install python-dotenv
```

Then, in your Python code, the environment variables will be automatically loaded from the `.env` file.

## AWS Lambda Functions

For AWS Lambda functions, the environment variables are automatically set by the CDK infrastructure code. The Lambda functions will use the environment variables set in the CDK stack.

## Frontend Configuration

For the frontend, you need to update the `aws-exports.js` file with the Cognito User Pool ID and Client ID. These values can be obtained from the CDK outputs after deploying the infrastructure.

## Security Considerations

- Do not hardcode sensitive values in your code
- Do not commit the `.env` file to version control
- Use AWS Secrets Manager or Parameter Store for production environments
- Regularly rotate your database credentials and other sensitive information 