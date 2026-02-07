"""
Redis Cache Registry - Manages multiple Redis connections and cache instances.
Inspired by common_order_taking's cache_wrapper pattern.
"""

from typing import Dict, Any
import redis.asyncio as aioredis
from redis.asyncio import Redis
import logging

logger = logging.getLogger(__name__)


class CacheRegistry:
    """
    Central registry for managing multiple Redis cache connections.

    Usage:
        # In main.py or service.py
        from app.cache.registry import cache_registry
        cache_registry.from_config(config["REDIS_CACHE_HOSTS"])

        # In cache classes
        class VendorCache(RedisCache):
            _host_label = "shaadi_on_track"
    """

    def __init__(self):
        self._hosts: Dict[str, Dict[str, Any]] = {}
        self._connections: Dict[str, Redis] = {}
        self._initialized = False

    def from_config(self, redis_config: Dict[str, Dict[str, Any]]):
        """
        Initialize Redis connections from configuration.

        Args:
            redis_config: Dictionary of Redis host configurations
                Example:
                {
                    "shaadi_on_track": {
                        "REDIS_HOST": "localhost",
                        "REDIS_PORT": 6379,
                        "REDIS_DB": 0,
                        "REDIS_PASSWORD": "",
                        "LABEL": "shaadi_on_track"
                    }
                }
        """
        if self._initialized:
            logger.warning(
                "CacheRegistry already initialized. Skipping re-initialization."
            )
            return

        self._hosts = redis_config
        logger.info(
            f"Registered {len(self._hosts)} Redis host(s): {list(self._hosts.keys())}"
        )
        self._initialized = True

    async def get_connection(self, label: str) -> Redis:
        """
        Get or create a Redis connection for the given label.

        Args:
            label: The host label (e.g., "shaadi_on_track")

        Returns:
            Redis: Async Redis connection
        """
        if label in self._connections:
            return self._connections[label]

        if label not in self._hosts:
            raise ValueError(
                f"Redis host '{label}' not found in registry. "
                f"Available hosts: {list(self._hosts.keys())}"
            )

        config = self._hosts[label]

        # Prefer full URL if provided (supports redis:// and rediss://)
        redis_url = config.get("REDIS_URL")
        if not redis_url:
            scheme = "rediss" if config.get("REDIS_SSL") else "redis"
            redis_url = (
                f"{scheme}://{config['REDIS_HOST']}:{config['REDIS_PORT']}/"
                f"{config.get('REDIS_DB', 0)}"
            )

        # NOTE: redis.asyncio.from_url() returns a Redis client instance (not a coroutine).
        # Do NOT await it. Only Redis commands like ping/get/set are awaited.
        connection = aioredis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            socket_keepalive=True,
            health_check_interval=30,
            retry_on_timeout=True,
            ssl_cert_reqs=None,
        )

        # Test connection
        try:
            await connection.ping()
            logger.info(
                f"Connected to Redis '{label}' at {config['REDIS_HOST']}:{config['REDIS_PORT']}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Redis '{label}': {e}")
            raise

        self._connections[label] = connection
        return connection

    async def close_all(self):
        """Close all Redis connections."""
        for label, conn in self._connections.items():
            try:
                await conn.close()
                logger.info(f"Closed Redis connection '{label}'")
            except Exception as e:
                logger.error(f"Error closing Redis connection '{label}': {e}")

        self._connections.clear()
        self._initialized = False

    def get_host_config(self, label: str) -> Dict[str, Any]:
        """Get configuration for a specific host label."""
        if label not in self._hosts:
            raise ValueError(
                f"Redis host '{label}' not found in registry. "
                f"Available hosts: {list(self._hosts.keys())}"
            )
        return self._hosts[label]


# Global cache registry instance
cache_registry = CacheRegistry()
