import React, { useState, useRef, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Snackbar, Alert } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DashboardIcon from '@mui/icons-material/Dashboard';
import HistoryIcon from '@mui/icons-material/History';
import LogoutIcon from '@mui/icons-material/Logout';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import { getToken, clearToken } from '../services/auth';
import { AuthContext } from '../App';
import '../styles/Sidebar.css';

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const { setAuthenticated } = useContext(AuthContext);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'text/csv') {
      setNotification({
        open: true,
        message: 'Please select a CSV file',
        severity: 'error',
      });
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        body: formData
      });

      if (response.status === 401) {
        throw new Error('Session expired. Please log in again.');
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to upload file');
      }

      setNotification({
        open: true,
        message: 'File uploaded successfully!',
        severity: 'success',
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload file';
      setNotification({
        open: true,
        message: `Upload failed: ${errorMessage}`,
        severity: 'error',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>SwolePT</h2>
      </div>
      <nav className="sidebar-nav">
        <div className="nav-section">
          <Link to="/dashboard" className="nav-item">
            <DashboardIcon />
            <span>Dashboard</span>
          </Link>
          <Link to="/get-swole" className="nav-item">
            <FitnessCenterIcon />
            <span>Get Swole</span>
          </Link>
          <div className="nav-item" onClick={() => fileInputRef.current?.click()}>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              ref={fileInputRef}
            />
            <CloudUploadIcon />
            <span>{uploading ? 'Uploading...' : 'Upload Workout'}</span>
          </div>
          <Link to="/workout-history" className="nav-item">
            <HistoryIcon />
            <span>Workout History</span>
          </Link>
        </div>
      </nav>
      <div className="sidebar-footer">
        <div 
          className="nav-item" 
          onClick={() => {
            clearToken();
            setAuthenticated(false);
            navigate('/login');
          }}
          style={{ cursor: 'pointer' }}
        >
          <LogoutIcon />
          <span>Logout</span>
        </div>
      </div>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </div>
  );
};

export default Sidebar; 