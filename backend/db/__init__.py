"""
Database package for SwolePT backend.
This package provides database functionality including models, migrations, and setup.
"""
from .setup import setup_database

__all__ = [
    'setup_database',
] 