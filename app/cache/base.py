"""
Base Redis Cache class - Similar to common_order_taking's RedisCache pattern.
"""

from typing import Optional, Any, List
from redis.asyncio import Redis
import json
import logging
from app.cache.registry import cache_registry

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Base class for Redis cache operations.

    Child classes should define:
        _service_prefix: Service name prefix for keys
        _host_label: Label of Redis host from registry
        _key_prefix: Optional additional key prefix

    Usage:
        class VendorCache(RedisCache):
            _service_prefix = "shaadi_on_track"
            _host_label = "shaadi_on_track"
            _key_prefix = "vendor"

        # Set cache
        await VendorCache.set("vendor:123", {"name": "ABC"}, expiry=300)

        # Get cache
        data = await VendorCache.get("vendor:123")
    """

    _service_prefix: str = ""
    _host_label: str = ""
    _key_prefix: str = ""

    @classmethod
    def _build_key(cls, key: str) -> str:
        """
        Build the full Redis key with prefixes.

        Args:
            key: Base key name

        Returns:
            str: Full key with prefixes (e.g., "shaadi_on_track:vendor:123")
        """
        parts = [p for p in [cls._service_prefix, cls._key_prefix, key] if p]
        return ":".join(parts)

    @classmethod
    async def _get_client(cls) -> Redis:
        """Get Redis client from registry."""
        if not cls._host_label:
            raise ValueError(f"{cls.__name__} must define _host_label")
        return await cache_registry.get_connection(cls._host_label)

    @classmethod
    async def set(
        cls, key: str, value: Any, expiry: Optional[int] = 300, serialize: bool = True
    ) -> bool:
        """
        Set a value in Redis cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized if serialize=True)
            expiry: Expiration time in seconds (None = no expiry)
            serialize: Whether to JSON serialize the value

        Returns:
            bool: True if successful
        """
        try:
            client = await cls._get_client()
            full_key = cls._build_key(key)

            # Serialize value if needed
            cache_value = json.dumps(value) if serialize else value

            # Set with or without expiry
            if expiry:
                await client.setex(full_key, expiry, cache_value)
            else:
                await client.set(full_key, cache_value)

            logger.debug(f"Cache SET: {full_key} (expiry: {expiry}s)")
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False

    @classmethod
    async def get(cls, key: str, deserialize: bool = True, default: Any = None) -> Any:
        """
        Get a value from Redis cache.

        Args:
            key: Cache key
            deserialize: Whether to JSON deserialize the value
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            client = await cls._get_client()
            full_key = cls._build_key(key)

            value = await client.get(full_key)

            if value is None:
                logger.debug(f"Cache MISS: {full_key}")
                return default

            logger.debug(f"Cache HIT: {full_key}")
            return json.loads(value) if deserialize else value
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return default

    @classmethod
    async def delete(cls, key: str) -> bool:
        """
        Delete a key from Redis cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key was deleted
        """
        try:
            client = await cls._get_client()
            full_key = cls._build_key(key)

            result = await client.delete(full_key)
            logger.debug(f"Cache DELETE: {full_key}")
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False

    @classmethod
    async def exists(cls, key: str) -> bool:
        """
        Check if a key exists in Redis cache.

        Args:
            key: Cache key

        Returns:
            bool: True if key exists
        """
        try:
            client = await cls._get_client()
            full_key = cls._build_key(key)

            result = await client.exists(full_key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False

    @classmethod
    async def expire(cls, key: str, seconds: int) -> bool:
        """
        Set expiry time for a key.

        Args:
            key: Cache key
            seconds: Expiry time in seconds

        Returns:
            bool: True if expiry was set
        """
        try:
            client = await cls._get_client()
            full_key = cls._build_key(key)

            result = await client.expire(full_key, seconds)
            logger.debug(f"Cache EXPIRE: {full_key} ({seconds}s)")
            return result
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False

    @classmethod
    async def keys(cls, pattern: str = "*") -> List[str]:
        """
        Get all keys matching a pattern.

        Args:
            pattern: Key pattern (e.g., "vendor:*")

        Returns:
            List of matching keys (without service prefix)
        """
        try:
            client = await cls._get_client()
            full_pattern = cls._build_key(pattern)

            keys = await client.keys(full_pattern)

            # Remove prefix from keys
            prefix_len = len(cls._build_key(""))
            return [
                k[prefix_len:] if k.startswith(cls._build_key("")) else k for k in keys
            ]
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern '{pattern}': {e}")
            return []

    @classmethod
    async def flush_pattern(cls, pattern: str = "*") -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Key pattern (e.g., "vendor:*")

        Returns:
            Number of keys deleted
        """
        try:
            client = await cls._get_client()
            full_pattern = cls._build_key(pattern)

            keys = await client.keys(full_pattern)
            if keys:
                deleted = await client.delete(*keys)
                logger.info(
                    f"Cache FLUSH: Deleted {deleted} keys matching '{full_pattern}'"
                )
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis FLUSH error for pattern '{pattern}': {e}")
            return 0
