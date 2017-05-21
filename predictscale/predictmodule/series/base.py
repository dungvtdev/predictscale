import pandas as pd


class Series(object):
    name = ''
    last = None
    data = None

    def __init__(self, **kwargs):
        super(Series, self).__init__()
        self.name = kwargs.get('name', None)

    def get_pandas_resample_char(self):
        raise NotImplementedError('get_pandas_resample_char must be implement')

    def append(self, points, last):
        if self.data is None:
            self.data = pd.Series(data=points)
            self.last = last
        else:
            self._append(points, last)

    def _append(self, points, last):
        l = last - self.last
        if len(points) > l:
            new = points[len(points) - l:]
        else:
            bu = [points[0]] * (l - len(points))
            bu.extend(points)
            new = bu
        if new:
            self.data = self.data.append(pd.Series(new), ignore_index=True)
            self.last = last

    # def append_secs(self, secs_tuple):
    #     if not secs_tuple:
    #         return
    #     d = pd.DataFrame(secs_tuple)
    #     d = d.set_index(d[0] * 1000000000)
    #     d_secs = d.set_index(pd.to_datetime(d.index))[1]
    #     d_min = d_secs.resample(self.get_pandas_resample_char()).mean()
    #     d_min = d_min.interpolate()

    #     last = d_min.index[-1].value / 1000000000
    #     self.append(d_min, last)

    def shift(self, n):
        pop = self.data[:n]
        new = pd.Series([])
        new = new.append(self.data[n:], ignore_index=True)
        del self.data
        self.data = new
        return pop

    # def get_values(self, indices):
    #     rl = [self.data.iloc[i] for i in indices]
    #     return rl

    def get_last(self):
        rl = self.data.iloc[-1]
        return rl


class SeriesMinute(Series):
    def get_last_max_seconds(self):
        return self.last_secs + 59

    def get_pandas_resample_char(self):
        return 'T'
