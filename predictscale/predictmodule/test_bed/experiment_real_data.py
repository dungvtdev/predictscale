import startup
from predictmodule.algorithm.predict import base
from predictmodule.algorithm.datafeeder import base as feeder_base

from predictmodule.datafetch import datacsv
from predictmodule.algorithm.datafeeder import experiment_feeder as ef

from sklearn.metrics import mean_squared_error
from predictmodule.algorithm.utils.GraphUtil import *
from math import sqrt
import numpy as np

n_input = 4
n_periodic = 1
n_hidden = 15
neural_shape = [n_input + n_periodic, n_hidden, 1]

cross_rate = 0.6
mutation_rate = 0.04
pop_size = 50


def normalize(data):
    return (data - data.min()) / (data.max() - data.min())


def unnormalize(data, minval, maxval):
    return data * (maxval - minval) + minval

k = 1

class ExperimentFeeder(feeder_base.BaseFeeder):
    def preprocess_data(self, data):
        return normalize(data)

    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        self.setup(n_input=n_input,
                   n_periodic=n_periodic,
                   period=period)
        data = self.data_fetch.fetch_series()
        range_train = (1 * period, 3 * period)
        return self.generate(data, range_train, k)

class ExperimentTestFeeder(feeder_base.BaseFeeder):
    def preprocess_data(self, data):
        self._max_val = data.max()
        self._min_val = data.min()
        return normalize(data)

    def postprocess_data(self, data):
        return unnormalize(data, self._min_val, self._max_val)

    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        self.setup(n_input=n_input,
                   n_periodic=n_periodic,
                   period=period)
        data = self.data_fetch.fetch_series()
        range_train = (3*period, 6*period)
        return self.generate(data, range_train, k)


def experiment_1():
    csv_reader = datacsv.CSVReader('data_vm.csv')
    predictor = base.Predictor(recent_point=n_input,
                               periodic_number=n_periodic,
                               neural_size=n_hidden,
                               period=56)

    rl = []
    for i in range(10):
        k = i+1

        feeder = ExperimentFeeder(csv_reader)
        predictor.train(feeder)

        test_feeder = ExperimentTestFeeder(csv_reader)
        o_pred, o = predictor.predict_test(test_feeder)
        o_pred = test_feeder.postprocess_data(o_pred)
        o = test_feeder.postprocess_data(o)
        print("done")
        if k == 1:
            rl.append(sqrt(mean_squared_error(o_pred, o)))
        else:
            b = []
            for j in range(k-1):
                b.append([o[j],])
            b = np.array(b)
            pred = np.concatenate((b, o_pred[k-1:]), axis=0)
            rl.append(sqrt(mean_squared_error(pred, o)))
            # plot_figure(pred, o)
    print(rl)

if __name__ == '__main__':
    experiment_1()
