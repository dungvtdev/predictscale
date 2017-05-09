from . import base


class ChunkSeries(base.SeriesMinute):
    def __init__(self, max_length=None, bias_length=None, **kwargs):
        super(ChunkSeries, self).__init__(**kwargs)
        self._max_length = max_length
        self._bias_length = bias_length

    def check_data_size(self):
        if len(self.data) - self._max_length > self._bias_length:
            self.shift(len(self.data) - self._max_length)

    def append(self, points, last_secs):
        super(ChunkSeries, self).append(points, last_secs)
        self.check_data_size()
