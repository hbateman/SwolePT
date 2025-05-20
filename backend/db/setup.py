"""
Database setup and initialization for SwolePT backend.
This module provides a single point for database initialization and migration.
"""
import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy_utils import database_exists, create_database
import logging
from pathlib import Path
from alembic.config import Config
from alembic import command
from .providers import get_provider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_connection(engine):
    """Test database connection by executing a simple query."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {str(e)}")
        return False

def verify_tables(engine):
    """Verify that all required tables exist."""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        required_tables = ['users', 'workout_history', 'alembic_version']
        
        logger.info(f"Found tables: {', '.join(existing_tables)}")
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        if missing_tables:
            logger.error(f"Missing required tables: {', '.join(missing_tables)}")
            return False
        
        logger.info(f"✅ Verified all required tables exist: {', '.join(existing_tables)}")
        return True
    except Exception as e:
        logger.error(f"Error verifying tables: {str(e)}")
        return False

def setup_database():
    """
    Set up the database and run migrations.
    This is the single entry point for database setup that:
    1. Creates the database if it doesn't exist
    2. Initializes the database with required tables
    3. Runs all pending migrations
    4. Verifies the setup was successful
    """
    try:
        # Get database URL from provider
        provider = get_provider()
        db_url = provider.get_connection_url()
        logger.info(f"Using database URL: {db_url}")
        
        # Test initial connection
        engine = create_engine(db_url)
        if not test_connection(engine):
            logger.error("Failed to connect to database")
            return False
        
        # Create database if it doesn't exist
        if not database_exists(db_url):
            logger.info("Creating database...")
            create_database(db_url)
            logger.info("Database created successfully")
        
        # Initialize database with required tables
        logger.info("Initializing database tables...")
        provider.init_db()
        logger.info("Database tables initialized successfully")
        
        # Run migrations
        logger.info("Running database migrations...")
        # Get paths
        backend_dir = Path(__file__).parent.parent
        alembic_ini_path = backend_dir / 'alembic.ini'
        migrations_dir = backend_dir / 'db' / 'migrations'
        
        logger.info(f"Using alembic.ini: {alembic_ini_path}")
        logger.info(f"Using migrations directory: {migrations_dir}")
        
        # Configure and run migrations
        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option('script_location', str(migrations_dir))
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
        
        # Verify tables were created
        logger.info("Verifying database setup...")
        if not verify_tables(engine):
            logger.error("Table verification failed")
            return False
        
        logger.info("✅ Database setup completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1) 