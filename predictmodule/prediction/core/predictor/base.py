from ..estimators.GAEstimator import GAEstimator
from ..estimators.NeuralFlow import NeuralFlowRegressor


class Predictor():

    def __init__(self, n_input=0, n_periodic=0, period=0, n_neural_hidden=0,
                 cross_rate=0.6, mutation_rate=0.04, pop_size=50):
        self._n_input = n_input
        self._n_periodic = n_periodic
        self._n_hidden = n_neural_hidden
        self._cross_rate = cross_rate
        self._mutation_rate = mutation_rate
        self._pop_size = pop_size
        self.period = period

    def train(self, dataFeeder):
        in_train, out_train = dataFeeder.fetch_training(
            self._n_input, self._n_periodic, self.period)

        gaEstimator = GAEstimator(cross_rate=self._cross_rate,
                                  mutation_rate=self._mutation_rate,
                                  pop_size=self._pop_size)

        neural_shape = [self._n_input + self._n_periodic, self._n_hidden, 1]
        fit_param = {
            "neural_shape": neural_shape
        }
        # return in_train, out_train
        gaEstimator.fit(in_train, out_train, **fit_param)
        fit_param["weights_matrix"] = gaEstimator.best_archive
        neuralNet = NeuralFlowRegressor()
        neuralNet.fit(in_train, out_train, **fit_param)
        self.neural = neuralNet
