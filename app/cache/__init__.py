"""
Cache module - Redis caching utilities.

Usage:
    from app.cache import VendorCache, CacheExpiry, cache_registry

    # In main.py startup
    cache_registry.from_config(config["REDIS_CACHE_HOSTS"])

    # In service managers
    await VendorCache.set(key, value, expiry=CacheExpiry.VENDOR_LIST.value)
"""

from app.cache.registry import cache_registry
from app.cache.base import RedisCache
from app.cache.vendor import VendorCache
from app.cache.service_category import ServiceCategoryCache
from app.cache.budget import BudgetCache

__all__ = [
    "cache_registry",
    "RedisCache",
    "VendorCache",
    "ServiceCategoryCache",
    "BudgetCache",
]
