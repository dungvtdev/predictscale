import pandas as pd
import numpy as np


# def normalize(data):
#     norm = (data - data.min()) / (data.max() - data.min())
#     return norm


# def unnormalize(data, min_val, max_val):
#     # max_val = self.workload.max()
#     # min_val = self.workload.min()
#     return data * (max_val - min_val) + min_val


class BaseFeeder():

    def __init__(self, data_fetch=None, **kwargs):
        self.data_fetch = data_fetch

        self.n_input = None
        self.n_periodic = None
        self.period = None
        self._max = None
        self._min = None

        self.setup(**kwargs)

    def setup(self, n_input=None, n_periodic=None, period=None):
        self.n_input = n_input or self.n_input
        self.n_periodic = n_periodic if n_periodic is not None \
            else self.n_periodic
        self.period = period or self.period

    def preprocess_data(self, data):
        raise NotImplementedError('Feeder need implement preprocess_data')

    def generate(self, data, range_data):
        data = self.preprocess_data(data)

        self._max = data.max()
        self._min = data.min()
        data = (data - self._min) / (self._max - self._min)

        period = self.period
        output_train = data[range_data[0]:range_data[1]]
        input_train = self.get_train_data(output_train, data)
        return np.asarray(input_train), np.asarray(output_train)

    def get_train_data(self, output_train, raw_data):
        training = []
        for r in range(output_train.index[0], output_train.index[-1] + 1):
            temp = []
            for p in range(0, self.n_input):
                temp.append(raw_data[r - p - 1])
            for m in range(1, self.n_periodic + 1):
                pval = raw_data[r - m * self.period]
                temp.append(pval)
            training.append(temp)
        return training

    def _normalize(self, data):
        if not isinstance(data, list):
            data = (data - self._min) / (self._max - self._min)
        else:
            for i in range(len(data)):
                data[i] = (data[i] - self._min) / (self._max - self._min)
        return data

    def _unnormalize(self, data):
        if not isinstance(data, list):
            return data * (self._max - self._min) + self._min
        else:
            for i in range(len(data)):
                data[i] = data[i] * (self._max - self._min) + self._min
            return data

    def generate_extend(self, data, extend):
        # idxs = list(range(0, self.n_input))
        idxs = []
        for m in range(1, self.n_periodic + 1):
            idxs.append(m * self.period)

        n_d = len(data)
        rl = [data[n_d - i - 1] for i in range(0, self.n_input)]
        n_ex = len(extend)
        for idx in idxs:
            if idx >= n_ex:
                rl.append(data[n_d - (idx - n_ex) - 1])
            else:
                rl.append(extend[-idx - 1])
        return rl

    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        pass
        # self.setup(n_input=n_input, n_periodic=n_periodic, period=period)
        # data = self.data_fetch.fetch_series()
        # max_periodic = int(len(data) / period)
