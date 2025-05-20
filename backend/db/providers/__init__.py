"""
Database providers package for SwolePT backend.
This package provides database provider implementations and factory.
"""
from .database_provider_factory import get_provider

__all__ = ['get_provider'] 