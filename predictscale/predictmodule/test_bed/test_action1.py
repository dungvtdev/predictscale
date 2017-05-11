import startup
from prediction.data.datafetch import influxdb
from prediction.data import utils
import pandas as pd
from prediction.data import training
from prediction.core.algorithm.predict import Predictor
from prediction.core.algorithm.datafeeder import SimpleFeeder
from prediction.data.datafetch import MemoryFetch

instance_meta = {
    'instance_id': 1,
    'action': {
        'period': 10,
        'n_period_to_train': 2,
        'n_predict': 3,
        'auto_retrain_period': 10,
    },
    'endpoint': '192.168.122.124',
    'db_name': 'cadvisor',
    'train_params': {
        'n_neural_hidden': 15,
        'n_input': 4,
        'n_periodic': 1,
    },
    'metric': 'cpu_usage_total',
}
config = {
    'n_input': 4,
    'n_periodic': 1,
    'period': 0,
    'n_neural_hidden': 15,
    'cross_rate': 0.6,
    'mutation_rate': 0.04,
    'pop_size': 50
}

instance_meta['epoch'] = 'm'

# fetch data to train

# print('start')
# last = influxdb.DiscoverLastTimeMinute(**instance_meta)()
# print(last)
# begin = influxdb.DiscoverBeginTimeMinute(**instance_meta)(last - 2000)
# print(begin)

# params = instance_meta
# params['batch_size'] = 4000
# cpu_fetch = influxdb.CpuFetch(**instance_meta)


# def filter(exdata):
#     print('filter')
#     print(exdata)
#     if pd.isnull(exdata).any():
#         isnull = pd.isnull(exdata)
#         idx = isnull[isnull == True].index.get_values()[-1]
#         print('filter %s %s' % (idx, True))
#         return exdata[idx + 1:], True
#     return exdata, False


# data = cpu_fetch.get_data(begin, last, filter=filter)
# print(data)
# print(len(data))

fetch_cls = influxdb.CpuFetch
data = training.get_available_dataframes(instance_meta, fetch_cls)
print(len(data))

# train data

n_input = 4
n_periodic = 1
n_hidden = 15
neural_shape = [n_input + n_periodic, n_hidden, 1]

cross_rate = 0.6
mutation_rate = 0.04
pop_size = 50
period = instance_meta['action']['period']

predictor = Predictor(n_input=n_input,
                      n_periodic=n_periodic,
                      n_neural_hidden=n_hidden,
                      period=period)
mem_fetch = MemoryFetch(data)
feeder = SimpleFeeder(mem_fetch)
predictor.train(feeder)

# get data and train window
