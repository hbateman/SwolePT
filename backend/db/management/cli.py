"""
Database management CLI for SwolePT backend.
This module provides command-line utilities for database management.
"""
#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command
from ..connection import init_db

def run_migrations():
    """Run database migrations using Alembic."""
    # Load environment variables
    load_dotenv()
    
    # Get the absolute path to the backend directory
    backend_dir = Path(__file__).parent.parent.parent
    alembic_ini_path = backend_dir / 'alembic.ini'
    
    if not alembic_ini_path.exists():
        print(f"❌ Error: alembic.ini not found at {alembic_ini_path}")
        sys.exit(1)
    
    # Create Alembic configuration
    alembic_cfg = Config(str(alembic_ini_path))
    
    # Set the script location in the config to point to our migrations directory
    migrations_dir = backend_dir / 'db' / 'migrations'
    alembic_cfg.set_main_option('script_location', str(migrations_dir))
    
    # Run migrations
    command.upgrade(alembic_cfg, "head")

def init_database():
    """Initialize the database with required tables."""
    init_db()

def main():
    """Main entry point for the database management CLI."""
    if len(sys.argv) != 2:
        print("Usage: python -m db.management.cli [init|migrate]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        print("Initializing database...")
        init_database()
        print("Database initialized successfully!")
    elif command == "migrate":
        print("Running migrations...")
        run_migrations()
        print("Migrations completed successfully!")
    else:
        print("Invalid command. Use 'init' or 'migrate'.")
        sys.exit(1)

if __name__ == "__main__":
    main() 