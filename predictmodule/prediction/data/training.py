import pandas as pd
from prediction.data.datafetch import influxdb
from . import utils
from ... import exceptions as ex
CONF = {
    'batch_size': 4000,
    'dataframe_size_bias': 0.1,
}


def filter(exdata):
    print('filter')
    if pd.isnull(exdata).any():
        isnull = pd.isnull(exdata)
        idx = isnull[isnull == True].tail().index.get_values()[0]
        print('filter %s %s' % (idx, True))
        return exdata[idx:], True
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
        raise ex.EndpointNotAvailable(str(instance_meta))

    dataframes = []

    begin = last_time - frame_minute
    begin = influxdb.DiscoverDataChunkStart(**instance_meta)(begin)

    data = fetch.get_data(begin, last_time, filter=filter)
    series = utils.time_series_to_pandas_series_minute(data, 'm')
    print(len(series))


def get_instance_metric_last_time(instance_meta):
    return influxdb.DiscoverLastTime(**instance_meta)()
