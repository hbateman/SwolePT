import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Amplify } from 'aws-amplify';
import awsconfig from './aws-exports';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import PrivateRoute from './components/PrivateRoute';
import { isAuthenticated } from './services/auth';
import './App.css';

// Configure Amplify with the unified configuration
Amplify.configure(awsconfig);

function App() {
  // Check if user is authenticated using our service
  const authenticated = isAuthenticated();
  console.log('App component - Authentication status:', authenticated);
  console.log('Environment:', process.env.REACT_APP_ENVIRONMENT);
  console.log('API URL:', process.env.REACT_APP_API_URL);
  console.log('Is local development:', process.env.REACT_APP_ENVIRONMENT === 'local');

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route 
            path="/dashboard" 
            element={
              <PrivateRoute isAuthenticated={authenticated}>
                <Dashboard />
              </PrivateRoute>
            } 
          />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 