from diskcache import Cache
from predictmodule import config as cf

cache = Cache(cf.cache_root)


def cache_data(key, value, expire=None):
    cache.set(key, value, expire=expire)


def get_cached_data(key):
    return cache.get(key)
