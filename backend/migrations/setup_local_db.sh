#!/bin/bash

# Script to set up a local development database for testing

# Set default values
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${DB_NAME:-"swolept"}
DB_USER=${DB_USER:-"postgres"}
DB_PASSWORD=${DB_PASSWORD:-"postgres"}

# Function to display usage
function show_usage {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  --host <host>              Database host (default: localhost)"
    echo "  --port <port>              Database port (default: 5432)"
    echo "  --name <name>              Database name (default: swolept)"
    echo "  --user <user>              Database user (default: postgres)"
    echo "  --password <password>      Database password (default: postgres)"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_usage
            exit 0
            ;;
        --host)
            DB_HOST="$2"
            shift 2
            ;;
        --port)
            DB_PORT="$2"
            shift 2
            ;;
        --name)
            DB_NAME="$2"
            shift 2
            ;;
        --user)
            DB_USER="$2"
            shift 2
            ;;
        --password)
            DB_PASSWORD="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Error: PostgreSQL is not installed or not in PATH"
    echo "Please install PostgreSQL and try again"
    exit 1
fi

# Create database if it doesn't exist
echo "Creating database $DB_NAME if it doesn't exist..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || true

# Export environment variables
export DATABASE_HOST=$DB_HOST
export DATABASE_PORT=$DB_PORT
export DATABASE_NAME=$DB_NAME
export DATABASE_USER=$DB_USER
export DATABASE_PASSWORD=$DB_PASSWORD

# Apply the initial migration
echo "Applying initial migration..."
python apply_migration.py 001_initial_schema.sql up

echo "Local development database setup complete!"
echo "Database: $DB_HOST:$DB_PORT/$DB_NAME (user: $DB_USER)"
echo ""
echo "To run migrations in the future, use:"
echo "  ./run_migrations.sh -u 001_initial_schema.sql"
echo ""
echo "To roll back migrations, use:"
echo "  ./run_migrations.sh -d 001_initial_schema_down.sql" 