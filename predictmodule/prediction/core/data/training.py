from prediction.data.datafetch import influxdb
from . import utils

CONF = {
    'batch_size': 4000,
    'dataframe_size_bias': 0.1,
    'dataframe_lookback_time_minute': 3000,
}


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
    lookback_time = config['dataframe_lookback_time_minute']
    dataframes = []

    size = lookback_time + frame_minute
    begin = last_time - size

    begin = influxdb.DiscoverDataChunkStart(**instance_meta)(begin)
    data = fetch.get_data(begin, last_time)
    series = utils.time_series_to_pandas_series_minute(data, 'm')
    print(len(series))


def get_instance_metric_last_time(instance_meta):
    return influxdb.DiscoverLastTime(**instance_meta)()
