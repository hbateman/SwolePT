-- Revert workout history table

-- Drop trigger first
DROP TRIGGER IF EXISTS update_workout_history_updated_at ON workout_history;

-- Drop table
DROP TABLE IF EXISTS workout_history; 