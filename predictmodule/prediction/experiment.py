from core.predictor import base
from datafetch import datacsv
from datafeeder import experiment_feeder as ef

from sklearn.metrics import mean_squared_error
from utils.GraphUtil import *
from math import sqrt


if __name__ == '__main__':
    n_input = 4
    n_periodic = 1
    n_hidden = 15
    period = 142
    neural_shape = [n_input + n_periodic, n_hidden, 1]

    cross_rate = 0.6
    mutation_rate = 0.04
    pop_size = 50

    csv_reader = datacsv.CSVReader('10min_workload.csv')
    predictor = base.Predictor(n_input=n_input,
                               n_periodic=n_periodic,
                               n_neural_hidden=n_hidden,
                               period=period)
    feeder = ef.ExperimentFeeder(csv_reader)
    predictor.train(feeder)

    test_feeder = ef.ExperimentTestFeeder(csv_reader)
    o_pred, o = predictor.predict_test(test_feeder)
    o_pred = test_feeder.postprocess_data(o_pred)
    o = test_feeder.postprocess_data(o)
    print("done")
    print(sqrt(mean_squared_error(o_pred, o)))
    plot_figure(o_pred, o)
