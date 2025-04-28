#!/bin/bash

# Script to run database migrations in a development environment

# Set default values
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${DB_NAME:-"swolept"}
DB_USER=${DB_USER:-"postgres"}
DB_PASSWORD=${DB_PASSWORD:-"postgres"}

# Export environment variables
export DATABASE_HOST=$DB_HOST
export DATABASE_PORT=$DB_PORT
export DATABASE_NAME=$DB_NAME
export DATABASE_USER=$DB_USER
export DATABASE_PASSWORD=$DB_PASSWORD

# Function to display usage
function show_usage {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help                 Show this help message"
    echo "  -u, --up <migration_file>  Run an up migration"
    echo "  -d, --down <migration_file> Run a down migration"
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
        -u|--up)
            MIGRATION_FILE="$2"
            DIRECTION="up"
            shift 2
            ;;
        -d|--down)
            MIGRATION_FILE="$2"
            DIRECTION="down"
            shift 2
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

# Check if migration file is provided
if [ -z "$MIGRATION_FILE" ]; then
    echo "Error: Migration file is required"
    show_usage
    exit 1
fi

# Check if migration file exists
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "Error: Migration file not found: $MIGRATION_FILE"
    exit 1
fi

# Run the migration
echo "Running $DIRECTION migration: $MIGRATION_FILE"
echo "Database: $DB_HOST:$DB_PORT/$DB_NAME (user: $DB_USER)"
python apply_migration.py "$MIGRATION_FILE" "$DIRECTION" 