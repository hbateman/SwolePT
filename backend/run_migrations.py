import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migrations():
    # Get database connection parameters
    db_params = {
        'dbname': 'swolept',  # Use the database we just created
        'user': os.getenv('DB_USER', 'hugo'),  # Default to current user if not specified
        'password': os.getenv('DB_PASSWORD', ''),  # Empty password for local development
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432')
    }

    # Connect to the database
    conn = psycopg2.connect(**db_params)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            # Read and execute the migration file
            with open('migrations/001_initial_schema.sql', 'r') as f:
                cur.execute(f.read())
            
            print("Migration completed successfully!")
    except Exception as e:
        print(f"Error running migration: {str(e)}")
    finally:
        conn.close()

if __name__ == '__main__':
    run_migrations() 