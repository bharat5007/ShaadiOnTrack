"""
Service category cache operations.
"""

from app.cache.base import RedisCache
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ServiceCategoryCache(RedisCache):
    _service_prefix = settings.SERVICE_NAME
    _host_label = "shaadi_on_track"
    _key_prefix = "service_category"
    _expire = 300

    @classmethod
    async def get_key(cls, key):
        return await cls.get(key)

    @classmethod
    async def set_key(cls, key, value, expire=None):
        expire = expire or cls._expire
        await cls.set(key, value)
