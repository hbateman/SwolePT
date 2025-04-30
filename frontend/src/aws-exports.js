// Determine if we're in a local development environment
const isLocalDevelopment = process.env.REACT_APP_ENVIRONMENT === 'local';

// Base configuration that works for both environments
const awsmobile = {
    "aws_project_region": process.env.AWS_REGION || (isLocalDevelopment ? "us-east-1" : "ap-southeast-2"),
    "aws_cognito_region": process.env.AWS_REGION || (isLocalDevelopment ? "us-east-1" : "ap-southeast-2"),
    "aws_user_pools_id": process.env.USER_POOL_ID || (isLocalDevelopment ? "local_user_pool" : "ap-southeast-2_r5ibADADi"),
    "aws_user_pools_web_client_id": process.env.USER_POOL_CLIENT_ID || (isLocalDevelopment ? "local_client" : "5t4tmpolgpctgq3s7kav2dk0o1"),
    "oauth": {},
    "federationTarget": "COGNITO_USER_POOLS",
    "aws_cognito_username_attributes": ["email"],
    "aws_cognito_social_providers": [],
    "aws_cognito_signup_attributes": ["email", "given_name", "family_name"],
    "aws_cognito_mfa_configuration": "OFF",
    "aws_cognito_mfa_types": [],
    "aws_cognito_password_protection_settings": {
        "passwordPolicyMinLength": 8,
        "passwordPolicyCharacters": []
    }
};

// Add LocalStack-specific configuration when in local development
if (isLocalDevelopment) {
    awsmobile.aws_appsync_graphqlEndpoint = process.env.AWS_ENDPOINT_URL || "http://localhost:4566";
    awsmobile.aws_appsync_region = process.env.AWS_REGION || "us-east-1";
    awsmobile.aws_appsync_authenticationType = "API_KEY";
    awsmobile.aws_appsync_apiKey = "local";
}

export default awsmobile; 