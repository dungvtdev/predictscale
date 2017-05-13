import pandas as pd
from .datafetch import influxdb
from . import utils
from .. import exceptions as ex
from predictmodule import DataMeta, datacache

CONF = {
    'batch_size': 4000,
    'dataframe_size_bias': 0.1,
}


def filter(exdata):
    if pd.isnull(exdata).any():
        isnull = pd.isnull(exdata)
        idx = isnull[isnull == True].index.get_values()[-1]
        print('filter %s %s' % (idx, True))
        return exdata[idx + 1:], True
    return exdata, False


def get_available_dataframes(instance_meta, fetch_class):
    config = CONF

    params = instance_meta
    params['batch_size'] = config['batch_size']
    fetch = fetch_class(**params)

    period = instance_meta['period']
    data_length = instance_meta['data_length']
    dataframe_size_bias = config['dataframe_size_bias']
    frame_minute = data_length
    frame_size_bias = dataframe_size_bias * frame_minute

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
    cached = datacache.get_cached_data_forever(data_meta)
    if cached:
        cached_last = cached.last_time
        if cached_last > begin:
            temp_begin = cached_last
            data = fetch.get_data(temp_begin, last_time, filter=filter)
            real_begin = last_time - len(data)
            if temp_begin < real_begin:
                # giua cache va real series co khoang trong
                data_meta.data = data
                data_meta.last_time = last_time
            else:
                print('from cache')
                cat_from = len(cached.data) - (cached_last - begin)
                data_meta = utils.concat_pandas_series(
                    cached.data, data, cat_from)
                data_meta.last_time = last_time

    if data_meta.data is None:
        data = fetch.get_data(begin, last_time, filter=filter)
        data_meta.data = data
        data_meta.last_time = last_time

    print('begin %s end %s' % (begin, last_time))

    datacache.cache_data_forever(data_meta)

    return data_meta


def get_instance_metric_last_time(instance_meta):
    return influxdb.DiscoverLastTimeMinute(**instance_meta)()


def get_instance_metric_begin_time(instance_meta, begin):
    return influxdb.DiscoverBeginTimeMinute(**instance_meta)(begin)
