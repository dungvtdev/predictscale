from diskcache import Cache

cache = Cache('/home/dungvt/cache')
cache.pop('forever:1:cpu_usage_total')
