"""
Graph checkpointers configuration.

This module provides different checkpointer implementations for LangGraph:
- Memory checkpointer for development
- Redis checkpointer for high-performance caching
- PostgreSQL checkpointer for production persistence

IMPORTANT: Lazy Imports Pattern
------------------------------
This module uses lazy imports to avoid import errors when optional dependencies
are not installed. The actual import happens inside the get_checkpointer() function.

Required Packages by Checkpointer Type:
- memory: No additional packages (uses langgraph built-in)
- redis: pip install langgraph-checkpoint-redis
- postgres: pip install langgraph-checkpoint-postgres

Usage:
    from lg_deploy.graph_checkpointers import get_checkpointer

    # Development (memory - no extra packages needed)
    checkpointer = get_checkpointer("memory")

    # Redis (requires: pip install langgraph-checkpoint-redis)
    checkpointer = get_checkpointer("redis", conn_string="redis://localhost:6379")

    # PostgreSQL (requires: pip install langgraph-checkpoint-postgres)
    checkpointer = get_checkpointer("postgres", conn_string="postgresql://user:pass@host:db")

Environment Variables (optional):
    LG_CHECKPOINTER_TYPE: Override checkpointer type
    LG_CHECKPOINTER_CONN_STRING: Override connection string
"""

from __future__ import annotations

import logging
from typing import Literal, Optional, Union


logger = logging.getLogger('lg_deploy.graph_checkpointers')

CheckpointerType = Literal["memory", "redis", "postgres"]


def get_checkpointer(
    checkpointer_type: CheckpointerType = "memory",
    *,
    conn_string: Optional[str] = None,
) -> Union["MemorySaver", "RedisSaver", "PostgresSaver"]:
    """
    Factory function to create a checkpointer.
    
    Args:
        checkpointer_type: Type of checkpointer to create.
            - "memory": In-memory checkpointer (development only)
            - "redis": Redis-based checkpointer (high-performance)
            - "postgres": PostgreSQL database checkpointer (production)
        conn_string: Connection string for database checkpointers.
            - For redis: redis://host:port (e.g., redis://localhost:6379)
            - For postgres: postgresql://user:pass@host:port/dbname
    
    Returns:
        A checkpointer instance.
    
    Raises:
        ValueError: If checkpointer_type is unknown or conn_string is missing.
        ImportError: If the required package for the checkpointer is not installed.
    
    Example:
        >>> from lg_deploy.graph_checkpointers import get_checkpointer
        >>> # Memory checkpointer (no extra packages needed)
        >>> cp = get_checkpointer("memory")
        >>> # Redis checkpointer (requires: pip install langgraph-checkpoint-redis)
        >>> cp = get_checkpointer("redis", conn_string="redis://localhost:6379")
    """
    if checkpointer_type == "memory":
        from langgraph.checkpoint.memory import MemorySaver
        logger.info("Creating in-memory checkpointer (development only)")
        return MemorySaver()
    
    elif checkpointer_type == "redis":
        try:
            from langgraph.checkpoint.redis import RedisSaver
        except ImportError:
            raise ImportError(
                "Redis checkpointer requires 'langgraph-checkpoint-redis' package. "
                "Install with: pip install langgraph-checkpoint-redis"
            )
        if not conn_string:
            raise ValueError(
                "Redis checkpointer requires conn_string. "
                "Example: redis://localhost:6379"
            )
        logger.info("Creating Redis checkpointer")
        return RedisSaver.from_conn_string(conn_string)
    
    elif checkpointer_type == "postgres":
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
        except ImportError:
            raise ImportError(
                "PostgreSQL checkpointer requires 'langgraph-checkpoint-postgres' package. "
                "Install with: pip install langgraph-checkpoint-postgres"
            )
        if not conn_string:
            raise ValueError(
                "PostgreSQL checkpointer requires conn_string. "
                "Example: postgresql://user:password@localhost:5432/langgraph"
            )
        logger.info("Creating PostgreSQL checkpointer")
        return PostgresSaver.from_conn_string(conn_string)
    
    else:
        raise ValueError(
            f"Unknown checkpointer type: {checkpointer_type}. "
            f"Valid types: memory, redis, postgres"
        )


class CheckpointerRegistry:
    """
    Registry for managing multiple checkpointers.
    
    Useful for applications that need to support different
    checkpointer types based on configuration.
    
    Example:
        >>> from lg_deploy.graph_checkpointers import registry
        >>> # Get a named checkpointer
        >>> cp = registry.get("redis_checkpointer", "redis", "redis://localhost:6379")
        >>> # Close when done
        >>> registry.close("redis_checkpointer")
    """
    
    def __init__(self):
        self._checkpointers: dict[str, Union["MemorySaver", "RedisSaver", "PostgresSaver"]] = {}
    
    def get(
        self, 
        name: str, 
        checkpointer_type: CheckpointerType = "memory",
        conn_string: Optional[str] = None
    ) -> Union["MemorySaver", "RedisSaver", "PostgresSaver"]:
        """Get or create a named checkpointer."""
        if name not in self._checkpointers:
            self._checkpointers[name] = get_checkpointer(checkpointer_type, conn_string=conn_string)
        return self._checkpointers[name]
    
    def close(self, name: str) -> bool:
        """Close a named checkpointer (for database checkpointers)."""
        if name in self._checkpointers:
            checkpointer = self._checkpointers[name]
            if hasattr(checkpointer, 'close'):
                checkpointer.close()
            del self._checkpointers[name]
            return True
        return False
    
    def close_all(self) -> None:
        """Close all database checkpointers."""
        # Use list() to avoid RuntimeError when dictionary changes during iteration
        for name in list(self._checkpointers.keys()):
            self.close(name)


# Global registry instance
registry = CheckpointerRegistry()


def get_checkpointer_from_env() -> Union["MemorySaver", "RedisSaver", "PostgresSaver"]:
    """
    Create a checkpointer based on environment variables.
    
    Environment variables:
        LG_CHECKPOINTER_TYPE: Type of checkpointer (memory, redis, postgres)
        LG_CHECKPOINTER_CONN_STRING: Database connection string
    
    Returns:
        A checkpointer instance.
    
    Raises:
        ImportError: If the required package is not installed.
    
    Example .env:
        LG_CHECKPOINTER_TYPE=postgres
        LG_CHECKPOINTER_CONN_STRING=postgresql://user:pass@localhost:5432/db
    """
    import os
    
    checkpointer_type: CheckpointerType = os.environ.get("LG_CHECKPOINTER_TYPE", "memory")
    conn_string = os.environ.get("LG_CHECKPOINTER_CONN_STRING", None)
    
    return get_checkpointer(checkpointer_type, conn_string=conn_string)
