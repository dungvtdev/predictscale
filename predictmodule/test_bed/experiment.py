import startup
from prediction.algorithm.predictor import base
from prediction.data.datafetch import datacsv
from prediction.data.datafeeder import experiment_feeder as ef

from sklearn.metrics import mean_squared_error
from prediction.utils.GraphUtil import *
from math import sqrt


n_input = 4
n_periodic = 1
n_hidden = 15
neural_shape = [n_input + n_periodic, n_hidden, 1]

cross_rate = 0.6
mutation_rate = 0.04
pop_size = 50


def experiment_1():
    csv_reader = datacsv.CSVReader('10min_workload.csv')
    predictor = base.Predictor(n_input=n_input,
                               n_periodic=n_periodic,
                               n_neural_hidden=n_hidden,
                               period=142)
    feeder = ef.ExperimentFeeder(csv_reader)
    predictor.train(feeder)

    test_feeder = ef.ExperimentTestFeeder(csv_reader)
    o_pred, o = predictor.predict_test(test_feeder)
    o_pred = test_feeder.postprocess_data(o_pred)
    o = test_feeder.postprocess_data(o)
    print("done")
    print(sqrt(mean_squared_error(o_pred, o)))
    plot_figure(o_pred, o)


def experiment_2():
    csv_reader = datacsv.CSVReader('1m.data.csv')
    predictor = base.Predictor(n_input=n_input,
                               n_periodic=n_periodic,
                               n_neural_hidden=n_hidden,
                               period=480)
    feeder = ef.ExperimentFeeder2(csv_reader)
    predictor.train(feeder)

    test_feeder = ef.ExperimentTestFeeder2(csv_reader)
    o_pred, o = predictor.predict_test(test_feeder)
    o_pred = test_feeder.postprocess_data(o_pred)
    o = test_feeder.postprocess_data(o)
    print("done")
    print(sqrt(mean_squared_error(o_pred, o)))
    plot_figure(o_pred, o)


if __name__ == '__main__':
    # csv_reader = datacsv.CSVReader('10min_workload.csv')
    # predictor = base.Predictor(n_input=n_input,
    #                            n_periodic=n_periodic,
    #                            n_neural_hidden=n_hidden,
    #                            period=142)
    # feeder = ef.ExperimentFeeder(csv_reader)
    # in_train, out_train = feeder.fetch_training(
    #     n_input, n_periodic, 142)

    # csv_reader = datacsv.CSVReader('1m.data.csv')
    # predictor = base.Predictor(n_input=n_input,
    #                            n_periodic=n_periodic,
    #                            n_neural_hidden=n_hidden,
    #                            period=480)
    # feeder = ef.ExperimentFeeder2(csv_reader)
    # in_train, out_train = feeder.fetch_training(
    #     n_input, n_periodic, 480)

    experiment_2()
