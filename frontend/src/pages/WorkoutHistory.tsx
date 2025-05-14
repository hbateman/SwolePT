import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import { WorkoutRecord, fetchWorkoutHistory } from '../services/workout';

const WorkoutHistory: React.FC = () => {
  const [workouts, setWorkouts] = useState<WorkoutRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadWorkoutHistory = async () => {
      try {
        const data = await fetchWorkoutHistory();
        setWorkouts(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load workout history');
      } finally {
        setLoading(false);
      }
    };

    loadWorkoutHistory();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const formatMetric = (value: number | null, unit: string | null) => {
    if (value === null) return '-';
    return `${value}${unit ? ` ${unit}` : ''}`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ mt: 4 }}>
          <Alert severity="error">{error}</Alert>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Workout History
        </Typography>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Exercise</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Weight</TableCell>
                <TableCell>Reps</TableCell>
                <TableCell>Distance</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Comment</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {workouts.map((workout) => (
                <TableRow key={workout.id}>
                  <TableCell>{formatDate(workout.date)}</TableCell>
                  <TableCell>{workout.exercise}</TableCell>
                  <TableCell>{workout.category}</TableCell>
                  <TableCell>{formatMetric(workout.weight, workout.weight_unit)}</TableCell>
                  <TableCell>{workout.reps || '-'}</TableCell>
                  <TableCell>{formatMetric(workout.distance, workout.distance_unit)}</TableCell>
                  <TableCell>{workout.time || '-'}</TableCell>
                  <TableCell>{workout.comment || '-'}</TableCell>
                </TableRow>
              ))}
              {workouts.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} align="center">
                    No workout history found. Upload your first workout using the sidebar!
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Container>
  );
};

export default WorkoutHistory; 