"""
Budget cache operations.
"""

from app.cache.base import RedisCache
from app.config import settings


class BudgetCache(RedisCache):
    _service_prefix = settings.SERVICE_NAME
    _host_label = "shaadi_on_track"
    _key_prefix = "budget"
    _expire = 300
