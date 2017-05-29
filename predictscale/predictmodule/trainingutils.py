import pandas as pd
from .datafetch import influxdb
from . import utils
from . import exceptions as ex
# from predictmodule import DataMeta, datacache
from predictmodule.models import DataMeta
from predictmodule.cache import datacache

CONF = {
    'batch_size': 8000,
    'dataframe_size_bias': 0.1,
}


def filter(exdata):
    if pd.isnull(exdata).any():
        isnull = pd.isnull(exdata)
        idx = isnull[isnull == True].index.get_values()[-1]
        # print('filter %s %s' % (idx, True))
        return exdata[idx + 1:], True
    return exdata, False


def get_fetch(instance_meta, fetch_class):
    config = CONF

    params = instance_meta
    params['batch_size'] = config['batch_size']
    fetch = fetch_class(**params)

    return fetch


def get_available_dataframes(instance_meta, fetch_class):
    fetch = get_fetch(instance_meta, fetch_class)

    # period = instance_meta['period']
    data_length = instance_meta['data_length']
    frame_minute = data_length

    last_time = get_instance_metric_last_time(instance_meta)
    if not last_time:
        raise ex.EndpointNotAvailable(
            'Cant get last time %s' % str(instance_meta))

    begin = last_time - frame_minute
    begin = get_instance_metric_begin_time(instance_meta, begin)
    if not begin:
        raise ex.EndpointNotAvailable(
            'Cant get begin time %s' % str(instance_meta))

    data_meta = DataMeta(**instance_meta)

    data = fetch.get_data(begin, last_time, filter=filter)
    data_meta.data = data
    data_meta.last_time = last_time

    # print('begin %s end %s' % (begin, last_time))

    datacache.cache_data_temp(data_meta)
    datacache.cache_data_forever(data_meta)

    return data_meta


def get_instance_metric_last_time(instance_meta):
    return influxdb.DiscoverLastTimeMinute(**instance_meta)()


def get_instance_metric_begin_time(instance_meta, begin):
    return influxdb.DiscoverBeginTimeMinute(**instance_meta)(begin)
