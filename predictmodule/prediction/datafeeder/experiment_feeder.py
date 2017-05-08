from . import base


class ExperimentFeeder(base.BaseFeeder):

    def preprocess_data(self, data):
        return base.normalize(data)

    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        self.setup(n_input=n_input,
                   n_periodic=n_periodic,
                   period=period)
        data = self.data_fetch.fetch_series()
        range_train = (40, 46)
        return self.generate(data, range_train)


class ExperimentTestFeeder(base.BaseFeeder):

    def preprocess_data(self, data):
        self._max_val = data.max()
        self._min_val = data.min()
        return base.normalize(data)

    def postprocess_data(self, data):
        return base.unnormalize(data, self._min_val, self._max_val)

    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        self.setup(n_input=n_input,
                   n_periodic=n_periodic,
                   period=period)
        data = self.data_fetch.fetch_series()
        range_train = (46, 48)
        return self.generate(data, range_train)
