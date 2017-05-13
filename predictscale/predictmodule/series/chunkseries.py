try:
    from . import base
except:
    import base


class ChunkSeries(base.SeriesMinute):
    _save_popdata = None

    def __init__(self, max_length=None, bias_length=None, **kwargs):
        super(ChunkSeries, self).__init__(**kwargs)
        self._max_length = max_length
        self._bias_length = bias_length
        self._save_popdata = kwargs.get('save_popdata', None)

    def check_data_size(self):
        if self.data.shape[0] - self._max_length > self._bias_length:
            pop = self.shift(len(self.data) - self._max_length)
            if pop is not None and self._save_popdata:
                self._save_popdata(pop)

    def append(self, points, last_secs):
        super(ChunkSeries, self).append(points, last_secs)
        self.check_data_size()
