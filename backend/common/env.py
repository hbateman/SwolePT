"""Centralized environment loading for the backend."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the workspace root from environment variable or default to current directory
WORKSPACE_ROOT = os.getenv('WORKSPACE_ROOT', os.getcwd())

# Track whether environment has been loaded
_environment_loaded = False

def load_environment():
    """
    Load environment variables from the appropriate .env file.
    This function is idempotent - it will only load the environment once.
    The environment file is determined by the ENVIRONMENT variable:
    - If ENVIRONMENT=local: loads .env.local
    - If ENVIRONMENT=prod: loads .env.prod
    - Otherwise: loads .env
    """
    global _environment_loaded
    
    if _environment_loaded:
        return

    # Determine which .env file to load based on ENVIRONMENT
    env = os.getenv('ENVIRONMENT', 'local')
    env_file = Path(WORKSPACE_ROOT) / f'.env.{env}'
    
    if not env_file.exists():
        env_file = Path(WORKSPACE_ROOT) / '.env'
    
    if not env_file.exists():
        raise FileNotFoundError(f"No environment file found at {env_file}")

    load_dotenv(env_file, override=True)
    _environment_loaded = True 