import React from 'react';
import { Box, Container, Typography } from '@mui/material';

const Dashboard: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        
        <Typography variant="body1" paragraph>
          Welcome to your SwolePT dashboard. Use the sidebar to navigate to different features.
        </Typography>
      </Box>
    </Container>
  );
};

export default Dashboard; 