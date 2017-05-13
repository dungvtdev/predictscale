import time
from . import exceptions as ex
from predictmodule.prediction.core.algorithm.predict import Predictor
from predictmodule.prediction.data.datafetch import CpuFetch, InMemoryFetch
from predictmodule.prediction.data import training
from predictmodule.prediction.core.algorithm.datafeeder import SimpleFeeder
from predictmodule import config
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
    return config.map_fetch_cls[metric]


class InstanceMonitorContainer(object):
    _last_time_have = None
    _last_time_real = None

    def __init__(self, instance_meta=None, **kwargs):
        self.instance_id = kwargs.get('instance_id', None)
        self.metric = kwargs.get('metric', None)
        self.setup(instance_meta)

    def setup(self, instance_meta):
        self._instance_meta = instance_meta or self._instance_meta

    def get_data(self):
        fetch_cls = get_fetch(self.metric)
        data_meta = training.get_available_dataframes(
            self._instance_meta, fetch_cls)
        # return DataMeta(data=data, last_time=last_time,
        #                 instance_id=self.instance_id, metric=self.metric)
        return data_meta

    def get_data_info_string(self):
        data_meta = self.get_data()
        msg_tmpl = 'Has {current}, need to wait about {more} more. Process: {percentage} %'
        current = len(data_meta.data)
        more = self._instance_meta['data_length'] - current
        if more < 0:
            more = 0
        current_s = time.strftime('%H:%M', time.gmtime(current * 60))
        more_s = time.strftime('%H:%M', time.gmtime(more * 60))
        percentage = current * 100 / (current + more)
        return msg_tmpl.format(current=current_s, more=more_s,
                               percentage=percentage)

    def push(self):
        source = 'cached'

        meta = self.get_instance_meta()
        data = self.prepare_data(source=source)

        n_input = meta['train_params']['n_input'] or config['n_input']
        n_neural_hidden = meta['train_params']['n_neural_hidden'] \
            or config['n_neural_hidden']
        n_periodic = meta['train_params']['n_periodic'] or config['n_periodic']
        cross_rate = config['cross_rate']
        mutation_rate = config['mutation_rate']
        pop_size = config['pop_size']
        period = meta['action']['period']

        predictor = Predictor(n_input=n_input,
                              n_periodic=n_periodic,
                              n_neural_hidden=n_neural_hidden,
                              period=period,
                              cross_rate=cross_rate,
                              mutation_rate=mutation_rate,
                              pop_size=pop_size)
        self.predictor = predictor

        # get data to train
        fetch_cls = get_fetch(self.metric)
        data = training.get_available_dataframes(instance_meta, fetch_cls)

        mem_fetch = InMemoryFetch(data)
        feeder = SimpleFeeder(mem_fetch)
