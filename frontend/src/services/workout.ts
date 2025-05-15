import { getToken } from './auth';

const API_URL = process.env.REACT_APP_API_URL;

export interface WorkoutRecord {
  id: number;
  date: string;
  exercise: string;
  category: string;
  weight: number | null;
  weight_unit: string | null;
  reps: number | null;
  distance: number | null;
  distance_unit: string | null;
  time: string | null;
  comment: string | null;
  created_at: string;
}

export const fetchWorkoutHistory = async (): Promise<WorkoutRecord[]> => {
  const token = await getToken();
  
  const response = await fetch(`${API_URL}/workout-history`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch workout history');
  }

  return await response.json();
}; 