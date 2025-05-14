import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection parameters
DB_HOST = os.getenv('DATABASE_HOST')
DB_PORT = os.getenv('DATABASE_PORT')
DB_NAME = os.getenv('RDS_DATABASE_NAME')
DB_USER = os.getenv('RDS_DATABASE_USER')
DB_PASSWORD = os.getenv('RDS_DATABASE_PASSWORD')

# Validate required environment variables
required_vars = {
    'DATABASE_HOST': DB_HOST,
    'DATABASE_PORT': DB_PORT,
    'RDS_DATABASE_NAME': DB_NAME,
    'RDS_DATABASE_USER': DB_USER,
    'RDS_DATABASE_PASSWORD': DB_PASSWORD
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required database environment variables: {', '.join(missing_vars)}")

# Create database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800  # Recycle connections after 30 minutes
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database."""
    Base.metadata.create_all(bind=engine) 