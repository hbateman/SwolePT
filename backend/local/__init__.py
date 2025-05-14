"""
Local development package for SwolePT backend.
This package contains all the local development specific code and utilities.
"""
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

__version__ = '1.0.0' 