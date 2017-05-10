import startup
from prediction.data.datafetch import influxdb
from prediction.data import utils

instance_meta = {
    'instance_id': 1,
    'action': {
        'period': 1440,
        'n_period_to_train': 7,
        'n_predict': 3,
        'auto_retrain_period': 10,
    },
    'endpoint': '192.168.122.124',
    'db_name': 'cadvisor',
    'train_params': None,
    'metric': 'cpu_usage_total',
}

instance_meta['epoch'] = 'm'

# fetch data to train
print('start')
last = influxdb.DiscoverLastTimeMinute(**instance_meta)()
print(last)
# fetch_cls = influxdb.CPUFetchLazy
# chunks = training.get_available_dataframes(instance_meta, fetch_cls)
# train data

# thread loop get data and predict
