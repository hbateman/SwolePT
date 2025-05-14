#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command
from database import init_db

def run_migrations():
    """Run database migrations using Alembic."""
    # Load environment variables
    load_dotenv()
    
    # Create Alembic configuration
    alembic_cfg = Config("migrations/alembic.ini")
    
    # Run migrations
    command.upgrade(alembic_cfg, "head")

def init_database():
    """Initialize the database with required tables."""
    init_db()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_db.py [init|migrate]")
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