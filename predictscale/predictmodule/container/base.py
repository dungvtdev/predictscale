import time
import datetime
from . import exceptions as ex
from predictmodule.algorithm.predict import Predictor
from predictmodule.datafetch import CpuFetch, InMemoryFetch
from predictmodule import trainingutils as training
from predictmodule.algorithm.datafeeder import SimpleFeeder
from predictmodule import config as CONF
from predictmodule.cache import datacache
from predictmodule.series.chunkseries import ChunkSeries
from predictmodule import config as conf

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
    _chunk_length_bias = 0.1

    def __init__(self, instance_meta=None, **kwargs):
        self._last_time_have = None
        self._last_time_real = None
        self._need_time = None
        self.fetch = None
        self.feeder = None
        self.predictor = None

        period = instance_meta['period']
        self.series = ChunkSeries(max_length=period + 1,
                                  bias_length=conf.chunk_series_length_bias)

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

        self.feeder = feeder
        # cache data
        datacache.cache_data_forever(data_meta)

        # generate series
        cat_idx = len(data_meta.data) - period
        self.series.append(data_meta.data[cat_idx:], data_meta.last_time)

        # add fetch object
        self.fetch = training.get_fetch(meta, fetch_cls)
        # data = [0.2, 0.3, 0.5, 0.4, 0.7]
        # print(predictor.predict(data))

    def __repr__(self):
        tmpl = 'container {name}:{metric}'
        return tmpl.format(name=self._instance_meta['instance_id'],
                           metric=self._instance_meta['metric'])

    def predict(self, tick_minute):
        self._last_time_real = self._last_time_real + tick_minute
        data, last = self.fetch.get_short_data_as_list(self._last_time_real)
        if data is not None:
            self.series.append(data, last)
            return self.predict_value_future(), True
        else:
            return None, False

    def _predict(self, input_data):
        return self.predictor.predict(input_data)

    def predict_value_future(self):
        predict_length = self._instance_meta['predict_length']
        wnd = []
        for i in range(predict_length):
            input_data = self.feeder.generate_extend(data=self.series.data,
                                                     extend=wnd, normalize=True)
            val = self._predict(input_data)
            if val:
                wnd.append(val[0][0])

        mean_val = sum(wnd) / len(wnd)
        mean_val = self.feeder._unnormalize(mean_val)
        max_val = self.feeder._unnormalize(max(wnd))
        # unormalize
        return max_val, mean_val
