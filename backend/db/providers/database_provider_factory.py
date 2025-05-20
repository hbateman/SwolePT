"""
Database provider factory for SwolePT backend.
This module provides a factory for creating and managing database provider instances.
It implements the singleton pattern to ensure only one provider instance exists at a time.
"""
import os
from typing import Optional
from .database_provider import DatabaseProvider
from .production_database_provider import ProductionDatabaseProvider
from .local_database_provider import LocalDatabaseProvider

_provider_instance: Optional[DatabaseProvider] = None

def get_provider() -> DatabaseProvider:
    """
    Get the appropriate database provider based on the environment.
    Uses singleton pattern to maintain a single provider instance.
    
    Returns:
        DatabaseProvider: The appropriate provider for the current environment.
        
    Raises:
        RuntimeError: If provider initialization fails.
    """
    global _provider_instance
    
    if _provider_instance is None:
        environment = os.getenv('ENVIRONMENT', 'local').lower()
        
        try:
            if environment == 'production':
                _provider_instance = ProductionDatabaseProvider()
            else:
                _provider_instance = LocalDatabaseProvider()
                
            # Initialize the provider
            _provider_instance.connect()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database provider: {str(e)}")
    
    return _provider_instance 