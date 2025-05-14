# Database Migrations

This directory contains the database migration files and tools for the SwolePT application, using SQLAlchemy and Alembic.

## Structure

- `versions/`: Contains all migration files
- `env.py`: Alembic environment configuration
- `script.py.mako`: Template for new migrations
- `alembic.ini`: Alembic configuration file

## Usage

The database setup and migrations are handled automatically by the build script:

```bash
./build.sh local setup
```

This will:
1. Create the database if it doesn't exist
2. Create tables if they don't exist
3. Set up Alembic migrations
4. Apply any pending migrations

## Creating New Migrations

When you make changes to the SQLAlchemy models in `models.py`, you can create a new migration:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

## Applying Migrations

Migrations are automatically applied during setup. If you need to apply migrations manually:

```bash
cd backend
alembic upgrade head
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
- Automatic timestamp updates via SQLAlchemy
- Appropriate indexes for common queries 