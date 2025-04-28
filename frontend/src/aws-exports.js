const awsmobile = {
    "aws_project_region": "us-east-1",
    "aws_cognito_region": "us-east-1",
    "aws_user_pools_id": "YOUR_USER_POOL_ID",
    "aws_user_pools_web_client_id": "YOUR_CLIENT_ID",
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

export default awsmobile; 