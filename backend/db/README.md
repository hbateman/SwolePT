# Database Package

This package contains all database-related code for the SwolePT backend.

## Structure

```
db/
├── __init__.py           # Package initialization and exports
├── connection.py         # Database connection management
├── models/              # SQLAlchemy models
│   ├── __init__.py     # Model exports
│   ├── user.py         # User model
│   └── workout.py      # Workout model
├── migrations/          # Database migrations
│   ├── env.py
│   └── versions/
└── management/         # Database management utilities
    ├── __init__.py
    └── cli.py         # Command-line interface
```

## Usage

### Database Connection

```python
from db import get_db, init_db

# Initialize database
init_db()

# Get database session
db = next(get_db())
```

### Models

```python
from db import User, WorkoutHistory

# Create a new user
user = User(
    user_id="123",
    username="john_doe",
    email="john@example.com",
    password_hash="hashed_password",
    given_name="John",
    family_name="Doe"
)

# Create a new workout
workout = WorkoutHistory(
    user_id="123",
    date="2024-03-20",
    exercise="Bench Press",
    category="Strength",
    weight=135,
    weight_unit="lbs",
    reps=10
)
```

### Database Management

Run database initialization:
```bash
python -m db.management.cli init
```

Run database migrations:
```bash
python -m db.management.cli migrate
```

## Environment Variables

The following environment variables are required:
- `DATABASE_HOST`: Database host
- `DATABASE_PORT`: Database port
- `RDS_DATABASE_NAME`: Database name
- `RDS_DATABASE_USER`: Database user
- `RDS_DATABASE_PASSWORD`: Database password 