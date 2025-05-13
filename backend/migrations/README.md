# Database Migrations

This directory contains the database migration files and tools for the SwolePT application.

## Structure

- `001_initial_schema.sql`: Contains the complete database schema
- `apply_migration.py`: Python script to apply migrations
- `README.md`: This file

## Usage

To apply the database schema:

```bash
# From the backend directory
python migrations/apply_migration.py migrations/001_initial_schema.sql up
```

## Schema Overview

The schema includes:

1. `users` table:
   - Stores user information
   - Uses UUID-like user_id as primary key
   - Includes username, email, and name fields

2. `workout_history` table:
   - Stores workout records
   - Links to users via user_id
   - Includes exercise details, metrics, and timestamps

Both tables include:
- `created_at` and `updated_at` timestamps
- Automatic timestamp updates via triggers
- Appropriate indexes for common queries

## Notes

- This is a simplified migration structure that drops and recreates tables
- No data retention is guaranteed when running migrations
- For development purposes only 