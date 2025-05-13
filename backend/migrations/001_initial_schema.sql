-- Initial database schema for SwolePT application

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    given_name VARCHAR(255) NOT NULL,
    family_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create workout_history table
CREATE TABLE IF NOT EXISTS workout_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id),
    date DATE NOT NULL,
    exercise VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    weight DECIMAL(10,2),
    weight_unit VARCHAR(10),
    reps INTEGER,
    distance DECIMAL(10,2),
    distance_unit VARCHAR(10),
    time VARCHAR(50),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_workout_history_user_id ON workout_history(user_id);
CREATE INDEX IF NOT EXISTS idx_workout_history_date ON workout_history(date);
CREATE INDEX IF NOT EXISTS idx_workout_history_exercise ON workout_history(exercise);

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update the updated_at column
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Create trigger to automatically update the updated_at column for workout_history
CREATE TRIGGER update_workout_history_updated_at
BEFORE UPDATE ON workout_history
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column(); 