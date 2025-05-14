import React, { useState } from 'react';
import { Button, Container, Typography, CircularProgress, Paper, Box } from '@mui/material';
import { analyzeWorkoutHistory } from '../services/openai';
import { getToken } from '../services/auth';
import '../styles/GetSwole.css';

interface AnalysisResponse {
  analysis: string;
  model?: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  refusal?: string;
  annotations?: any[];
}

const GetSwole: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyzeWorkoutHistory = async () => {
    setLoading(true);
    setError(null);
    setAnalysis(null);

    try {
      const token = getToken();
      if (!token) {
        throw new Error('Not authenticated');
      }

      // Fetch workout history
      const response = await fetch(`${process.env.REACT_APP_API_URL}/workout-history`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });

      if (response.status === 401) {
        throw new Error('Session expired. Please log in again.');
      }

      const workoutHistory = await response.json();

      if (!response.ok) {
        throw new Error(workoutHistory.error || 'Failed to fetch workout history');
      }

      // Analyze workout history using OpenAI
      const analysisResult = await analyzeWorkoutHistory(workoutHistory);
      setAnalysis(analysisResult);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      if (errorMessage.includes('rate limit exceeded')) {
        setError('OpenAI API rate limit exceeded. Please wait a few minutes and try again.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" className="get-swole-container">
      <Typography variant="h4" component="h1" gutterBottom>
        Get Swole Analysis
      </Typography>
      
      <Button
        variant="contained"
        color="primary"
        onClick={handleAnalyzeWorkoutHistory}
        disabled={loading}
        className="analyze-button"
      >
        {loading ? <CircularProgress size={24} /> : 'Analyze Workout History'}
      </Button>

      {error && (
        <Paper className="error-paper" sx={{ mt: 2, p: 2, bgcolor: 'error.light' }}>
          <Typography color="error" variant="body1">
            {error}
          </Typography>
          {error.includes('rate limit exceeded') && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              This is a temporary limitation. Please wait a few minutes before trying again.
            </Typography>
          )}
        </Paper>
      )}

      {analysis && (
        <Box className="analysis-container">
          <Paper className="analysis-paper">
            <Typography variant="h6" gutterBottom>
              Analysis Results
            </Typography>
            <Typography variant="body1" paragraph>
              {analysis.analysis}
            </Typography>
            
            {analysis.model && (
              <Typography variant="caption" color="textSecondary">
                Model: {analysis.model}
              </Typography>
            )}
            
            {analysis.usage && (
              <Box mt={1}>
                <Typography variant="caption" color="textSecondary" display="block">
                  Token Usage:
                </Typography>
                <Typography variant="caption" color="textSecondary" display="block">
                  Prompt: {analysis.usage.prompt_tokens} | 
                  Completion: {analysis.usage.completion_tokens} | 
                  Total: {analysis.usage.total_tokens}
                </Typography>
              </Box>
            )}
            
            {analysis.refusal && (
              <Typography variant="caption" color="error" display="block">
                Refusal Reason: {analysis.refusal}
              </Typography>
            )}
          </Paper>
        </Box>
      )}
    </Container>
  );
};

export default GetSwole; 