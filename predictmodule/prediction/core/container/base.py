from . import exceptions as ex
from ..algorithm.predict import Predictor
from ...data.datafetch import CPUFetch
from ...data import training, MemoryFetch
from ..algorithm.datafeeder import SimpleFeeder

config = {
    'n_input': 4,
    'n_periodic': 1,
    'period': 0,
    'n_neural_hidden': 15,
    'cross_rate': 0.6,
    'mutation_rate': 0.04,
    'pop_size': 50
}

map_fetch_cls = {
    'cpu_usage_total': CPUFetch,
}


def get_fetch(metric):
    return map_fetch_cls[metric]


class DataMeta:
    source = 'cached' or 'remote'
    data = None
    last_time = None

    def __init__(self, **kwargs):
        self.source = kwargs.get('source', None)
        self.data = kwargs.get('data', None)
        self.last_time = kwargs.get('last_time', None)


class ContainerState:
    Initialize,
    PendingData,
    PendingUser,
    Pushing,
    Running,


class InstanceMonitorContainer(object):
    def __init__(self, backend, **kwargs):
        self.instance_id = kwargs.get('instance_id', None)
        self.metric = kwargs.get('metric', None)
        self.backend = backend
        self._instance_meta = None

    def get_instance_meta(self):
        if self.instance_id is None or self.metric is None:
            raise ex.InstanceContainerInternalError(
                'instance_id or metric not defined')
        if not self._instance_meta:
            self._instance_meta = backend.get_instance_meta(
                self.instance_id, self.metric)
        return self._instance_meta

    def prepare_data(self, source=None):
        meta = self.get_instance_meta()
        if source:
            return self._get_data(source)
        else:
            return {
                'cached': self._get_data('cached'),
                'remote': self._get_data('remote'),
            }

    def _get_data(self, source):
        fn = getattr(self, '_get_{source}_data'.format(source=source))
        return fn()

    def _get_cached_data(self):
        return DataMeta()

    def _get_remote_data(self):
        return DataMeta()

    def push(self):
        meta = self.get_instance_meta()
        data = self.prepare_data()

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

        mem_fetch = MemoryFetch(data)
        feeder = SimpleFeeder(mem_fetch)
