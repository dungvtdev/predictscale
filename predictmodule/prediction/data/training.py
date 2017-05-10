import pandas as pd
from .datafetch import influxdb
from . import utils
from .. import exceptions as ex
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

    action_params = instance_meta['action']
    period = action_params['period']
    n_period_to_train = action_params['n_period_to_train']
    dataframe_size_bias = config['dataframe_size_bias']
    frame_minute = period * n_period_to_train
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
    data = fetch.get_data(begin, last_time, filter=filter)

    return data


def get_instance_metric_last_time(instance_meta):
    return influxdb.DiscoverLastTimeMinute(**instance_meta)()


def get_instance_metric_begin_time(instance_meta, begin):
    return influxdb.DiscoverBeginTimeMinute(**instance_meta)(begin)
