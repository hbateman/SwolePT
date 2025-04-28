import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { StorageStack } from '../lib/storage-stack';
import { AuthStack } from '../lib/auth-stack';
import { ApiStack } from '../lib/api-stack';

describe('Infrastructure Stack', () => {
  const app = new cdk.App();
  // Create the stacks
  const storageStack = new StorageStack(app, 'SwolePTStorageStack');
  const authStack = new AuthStack(app, 'SwolePTAuthStack');
  const apiStack = new ApiStack(app, 'SwolePTApiStack', {
    vpc: storageStack.vpc,
    database: storageStack.database,
    bucket: storageStack.bucket,
    userPool: authStack.userPool,
    userPoolClient: authStack.userPoolClient,
  });

  // Add dependencies
  apiStack.addDependency(storageStack);
  apiStack.addDependency(authStack);

  // Test the storage stack
  const storageTemplate = Template.fromStack(storageStack);
  test('Storage Stack Created', () => {
    storageTemplate.templateMatches({
      Resources: {
        // Add expected resources here
      }
    });
  });

  // Test the auth stack
  const authTemplate = Template.fromStack(authStack);
  test('Auth Stack Created', () => {
    authTemplate.templateMatches({
      Resources: {
        // Add expected resources here
      }
    });
  });

  // Test the API stack
  const apiTemplate = Template.fromStack(apiStack);
  test('API Stack Created', () => {
    apiTemplate.templateMatches({
      Resources: {
        // Add expected resources here
      }
    });
  });
});
