import { getToken } from './auth';

interface WorkoutHistory {
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

interface OpenAIResponse {
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

export const analyzeWorkoutHistory = async (workoutHistory: WorkoutHistory[]): Promise<OpenAIResponse> => {
  const token = getToken();
  if (!token) {
    throw new Error('Not authenticated');
  }

  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL}/analyze-workouts`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ workoutHistory })
    });

    if (response.status === 401) {
      throw new Error('Session expired. Please log in again.');
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'Failed to analyze workout history');
    }

    return data;
  } catch (error) {
    console.error('Error analyzing workout history:', error);
    throw error;
  }
}; 