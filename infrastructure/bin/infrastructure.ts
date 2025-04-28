#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { ApiStack } from '../lib/api-stack';
import { StorageStack } from '../lib/storage-stack';
import { AuthStack } from '../lib/auth-stack';
import { FrontendStack } from '../lib/frontend-stack';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables from .env file
try {
  dotenv.config({ path: path.resolve(__dirname, '../.env') });
  console.log('Loaded environment variables from .env file');
} catch (error) {
  console.warn('Could not load .env file:', error);
}

const app = new cdk.App();

// Create the storage stack first
const storageStack = new StorageStack(app, 'SwolePTStorageStack', {
  env: {
    account: process.env.AWS_ACCOUNT_ID || process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.AWS_REGION || process.env.CDK_DEFAULT_REGION,
  },
});

// Create the auth stack
const authStack = new AuthStack(app, 'SwolePTAuthStack', {
  env: {
    account: process.env.AWS_ACCOUNT_ID || process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.AWS_REGION || process.env.CDK_DEFAULT_REGION,
  },
});

// Create the API stack last as it depends on both storage and auth
const apiStack = new ApiStack(app, 'SwolePTApiStack', {
  env: {
    account: process.env.AWS_ACCOUNT_ID || process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.AWS_REGION || process.env.CDK_DEFAULT_REGION,
  },
  vpc: storageStack.vpc,
  database: storageStack.database,
  bucket: storageStack.bucket,
  userPool: authStack.userPool,
  userPoolClient: authStack.userPoolClient,
});

// Create the frontend stack
const frontendStack = new FrontendStack(app, 'SwolePTFrontendStack', {
  env: {
    account: process.env.AWS_ACCOUNT_ID || process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.AWS_REGION || process.env.CDK_DEFAULT_REGION,
  },
  userPool: authStack.userPool,
  userPoolClient: authStack.userPoolClient,
  apiUrl: `https://${apiStack.restApi.restApiId}.execute-api.${process.env.AWS_REGION || process.env.CDK_DEFAULT_REGION}.amazonaws.com/${process.env.API_STAGE_NAME || 'prod'}`,
});

// Add dependencies to ensure proper deployment order
apiStack.addDependency(storageStack);
frontendStack.addDependency(apiStack);
frontendStack.addDependency(authStack);
