import { signIn, signUp, confirmSignUp } from 'aws-amplify/auth';

// Check if we're in a local development environment
const isLocalDevelopment = process.env.REACT_APP_ENVIRONMENT === 'local';

// Validate required environment variables
if (!process.env.REACT_APP_API_URL) {
  throw new Error('REACT_APP_API_URL environment variable is required but not set');
}

const API_URL = process.env.REACT_APP_API_URL;

// Local authentication functions
const localLogin = async (email: string, password: string) => {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Failed to login');
  }

  return data;
};

const localRegister = async (email: string, password: string, name: string) => {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, name }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || 'Failed to register');
  }

  return data;
};

// AWS Cognito authentication functions
const cognitoLogin = async (username: string, password: string) => {
  const result = await signIn({ username, password });
  
  // For Cognito, we need to get the session to access the tokens
  // This is a simplified version - in a real app, you'd want to handle the session properly
  return {
    token: 'cognito-token-placeholder', // In a real app, you'd get this from the session
    user: {
      email: username,
      id: 'cognito-user-id', // In a real app, you'd get this from the session
    },
  };
};

const cognitoRegister = async (email: string, password: string, name: string) => {
  const result = await signUp({
    username: email,
    password,
    options: {
      userAttributes: {
        email,
        name,
      },
    },
  });

  return {
    token: '',
    user: {
      email,
      id: result.userId,
    },
    requiresConfirmation: true,
  };
};

const cognitoConfirmRegistration = async (username: string, code: string) => {
  await confirmSignUp({
    username,
    confirmationCode: code,
  });
};

// Export the appropriate authentication functions based on environment
export const login = isLocalDevelopment ? localLogin : cognitoLogin;
export const register = isLocalDevelopment ? localRegister : cognitoRegister;
export const confirmRegistration = isLocalDevelopment ? 
  async () => {} : // No-op for local development
  cognitoConfirmRegistration;

// Helper function to check if user is authenticated
export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

// Helper function to get the authentication token
export const getToken = () => {
  return awaitlocalStorage.getItem('token');
};

// Helper function to set the authentication token
export const setToken = (token: string) => {
  localStorage.setItem('token', token);
};

// Helper function to clear the authentication token
export const clearToken = () => {
  localStorage.removeItem('token');
}; 