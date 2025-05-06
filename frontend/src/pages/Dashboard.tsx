import React, { useState } from 'react';
import { Box, Container, Typography, Paper, Snackbar, Alert } from '@mui/material';
import FileUpload from '../components/FileUpload';

const Dashboard: React.FC = () => {
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  const handleUploadSuccess = (fileKey: string) => {
    console.log('File uploaded successfully:', fileKey);
    setNotification({
      open: true,
      message: 'File uploaded successfully!',
      severity: 'success',
    });
  };

  const handleUploadError = (error: string) => {
    console.error('Upload error:', error);
    setNotification({
      open: true,
      message: `Upload failed: ${error}`,
      severity: 'error',
    });
  };

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        
        <Paper sx={{ p: 3, mb: 3 }}>
          <FileUpload
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />
        </Paper>
      </Box>

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
    </Container>
  );
};

export default Dashboard; 