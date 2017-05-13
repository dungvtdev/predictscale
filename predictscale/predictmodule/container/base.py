import time
import datetime
from . import exceptions as ex
from predictmodule.algorithm.predict import Predictor
from predictmodule.datafetch import CpuFetch, InMemoryFetch
from predictmodule import trainingutils as training
from predictmodule.algorithm.datafeeder import SimpleFeeder
from predictmodule import config as CONF

# config = {
#     'recent_point': 4,
#     'periodic_number': 1,
#     'period': 0,
#     'neural_size': 15,
#     'cross_rate': 0.6,
#     'mutation_rate': 0.04,
#     'pop_size': 50
# }

# map_fetch_cls = {
#     'cpu_usage_total': CpuFetch,
# }


def get_fetch(metric):
    return CONF.map_fetch_cls[metric]


class InstanceMonitorContainer(object):
    _last_time_have = None
    _last_time_real = None
    _need_time = None

    _chunk_length_bias = 0.1

    def __init__(self, instance_meta=None, **kwargs):
        self.instance_id = kwargs.get('instance_id', None)
        self.metric = kwargs.get('metric', None)
        self.setup(instance_meta)

    def setup(self, instance_meta):
        self._instance_meta = instance_meta or self._instance_meta

    def setup_wait(self):
        data_length = self._instance_meta['data_length']
        data_meta = self.get_data()

        self._last_time_have = data_meta.last_time
        self._last_time_real = self._last_time_have
        self._need_time = data_length - len(data_meta.data)
        if self._need_time < 0:
            self._need_time = 0

    def get_data(self):
        fetch_cls = get_fetch(self.metric)
        data_meta = training.get_available_dataframes(
            self._instance_meta, fetch_cls)
        # return DataMeta(data=data, last_time=last_time,
        #                 instance_id=self.instance_id, metric=self.metric)
        return data_meta

    def check_time_to_run(self, tick_minute=0):
        self._last_time_real = self._last_time_real + tick_minute
        return self._last_time_real >= \
            (self._last_time_have + self._need_time * (1 - self._chunk_length_bias))

    def get_data_info_string(self, data_meta=None):
        if data_meta is None:
            data_meta = self.get_data()
        msg_tmpl = 'Has {current} of data, need to wait about {more} more. Process: {percentage} %'
        current = len(data_meta.data)
        more = self._instance_meta['data_length'] - current
        if more < 0:
            more = 0
        current_s = str(datetime.timedelta(minutes=current))
        more_s = str(datetime.timedelta(minutes=more))
        percentage = current * 100 / (current + more)
        return msg_tmpl.format(current=current_s, more=more_s,
                               percentage=percentage)

    def push(self):
        meta = self._instance_meta
        data_meta = self.get_data()

        config = CONF.instance_meta_default

        recent_point = meta['recent_point'] or config['recent_point']
        neural_size = meta['neural_size'] or config['neural_size']
        periodic_number = meta['periodic_number'] or config['periodic_number']
        cross_rate = config['cross_rate']
        mutation_rate = config['mutation_rate']
        pop_size = config['pop_size']
        period = meta['period']

        predictor = Predictor(recent_point=recent_point,
                              periodic_number=periodic_number,
                              neural_size=neural_size,
                              period=period,
                              cross_rate=cross_rate,
                              mutation_rate=mutation_rate,
                              pop_size=pop_size)
        self.predictor = predictor

        # get data to train
        fetch_cls = get_fetch(self.metric)
        data_meta = training.get_available_dataframes(meta, fetch_cls)

        mem_fetch = InMemoryFetch(data_meta.data)
        feeder = SimpleFeeder(mem_fetch)
        predictor.train(feeder)
        # data = [0.2, 0.3, 0.5, 0.4, 0.7]
        # print(predictor.predict(data))

    def __repr__(self):
        tmpl = 'container {name}:{metric}'
        return tmpl.format(name=self._instance_meta['instance_id'],
                           metric=self._instance_meta['metric'])

    def predict(self):
        return 'test_val'


class FakeContainer():
    _last_time_have = None
    _last_time_real = None
    _need_time = None

    def __init__(self, instance_meta=None, **kwargs):
        self.instance_id = kwargs.get('instance_id', None)
        self.metric = kwargs.get('metric', None)
        self.setup(instance_meta)

    def setup(self, instance_meta):
        self._instance_meta = instance_meta or self._instance_meta
