from . import fscache as cache
from predictmodule import config as cf


def _get_key_string(data_meta, namespace=None):
    key_tmpl = '{namespace}:{id}:{metric}'
    namespace = namespace or 'df'
    key = key_tmpl.format(namespace=namespace,
                          id=data_meta.instance_id,
                          metric=data_meta.metric)
    return key


def cache_data_temp(data_meta):
    key = _get_key_string(data_meta, 'temp')
    expire = cf.expire
    cache.cache_data(key, data_meta, expire=expire)

    print('cache temp key={key}'.format(key=key))


def cache_data_forever(data_meta):
    key = _get_key_string(data_meta, 'forever')
    cache.cache_data(key, data_meta)

    print('cache forever key={key}'.format(key=key))


def get_cached_data_temp(data_meta):
    key = _get_key_string(data_meta, 'temp')
    return cache.get_cached_data(key)


def get_cached_data_forever(data_meta):
    key = _get_key_string(data_meta, 'forever')
    return cache.get_cached_data(key)
