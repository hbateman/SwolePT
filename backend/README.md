# SwolePT Backend

This directory contains the backend code for the SwolePT application, which is built using AWS Lambda functions and a PostgreSQL database.

## Directory Structure

- `common/`: Common utilities and modules shared across Lambda functions
- `functions/`: Lambda function handlers
  - `auth/`: Authentication-related functions (login, register, etc.)
  - `workouts/`: Workout management functions (create, list, update, delete)
  - `exercises/`: Exercise management functions
  - `users/`: User profile management functions
- `migrations/`: Database migration scripts
- `tests/`: Test files for the backend

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (for local development)
- AWS CLI configured with appropriate credentials

### Local Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up a local database:
   ```bash
   cd migrations
   ./setup_local_db.sh
   ```

4. Set environment variables for local development:
   ```bash
   export DATABASE_HOST=localhost
   export DATABASE_PORT=5432
   export DATABASE_NAME=swolept
   export DATABASE_USER=postgres
   export DATABASE_PASSWORD=postgres
   export USER_POOL_ID=your-cognito-user-pool-id
   export USER_POOL_CLIENT_ID=your-cognito-client-id
   ```

### Running Tests

```bash
python -m pytest tests/
```

## Deployment

The backend is deployed using AWS CDK. See the `infrastructure/` directory for deployment instructions.

## API Documentation

### Authentication Endpoints

- `POST /auth`: Authenticate a user
  - Actions: `login`, `register`, `confirm`, `refresh`

### Workout Endpoints

- `POST /workouts`: Manage workouts
  - Actions: `create`, `list`, `get`, `update`, `delete`

### Exercise Endpoints

- `POST /exercises`: Manage exercises
  - Actions: `create`, `list`, `get`, `update`, `delete`

### User Endpoints

- `POST /users`: Manage user profiles
  - Actions: `get`, `update` 