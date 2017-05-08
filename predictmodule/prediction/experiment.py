from core.predictor import base
from datafetch import datacsv
from datafeeder import experiment_feeder as ef

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
