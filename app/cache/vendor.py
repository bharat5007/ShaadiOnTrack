"""
Vendor cache operations - Caching for vendor-related data.
"""

from app.cache.base import RedisCache
from app.config import settings


class VendorCache(RedisCache):
    _service_prefix = settings.SERVICE_NAME
    _host_label = "shaadi_on_track"
    _key_prefix = "vendor"
    _expire = 300  # 5 minutes default TTL

    @classmethod
    async def get_key(cls, key: str):
        """Get a cached value by key."""
        return await cls.get(key)

    @classmethod
    async def set_key(cls, key: str, value, expire=None):
        """Set a cached value with optional custom expiry."""
        expire = expire or cls._expire
        await cls.set(key=key, value=value, expiry=expire)

    @classmethod
    async def delete_key(cls, key):
        await cls.delete(key)
