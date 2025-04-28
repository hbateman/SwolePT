-- Add workout history table

-- Create workout_history table
CREATE TABLE IF NOT EXISTS workout_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(user_id),
    file_name VARCHAR(255) NOT NULL,
    file_key VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add trigger for updated_at column
CREATE TRIGGER update_workout_history_updated_at
    BEFORE UPDATE ON workout_history
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 