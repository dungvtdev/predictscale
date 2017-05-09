import pandas as pd


class Series(object):
    name = ''
    last_secs = None
    data = None

    # bien phia tren cua series, dung de query series tiep theo
    def get_last_max_seconds(self):
        raise NotImplementedError('get_last_max_seconds must be implement')

    def get_pandas_resample_char(self):
        raise NotImplementedError('get_pandas_resample_char must be implement')

    def append(self, points, last_secs):
        if self.data is None:
            self.data = pd.Series(data=points)
            self.last_secs = last_secs
        else:
            self._append(points, last_secs)

    def _append(self, points, last_secs):
        l = last_secs - self.last_secs
        if len(points) > l:
            new = points[len(points) - l:]
        else:
            bu = [points[0]] * (l - len(points))
            bu.extend(points)
            new = bu
        if new:
            self.data = self.data.append(pd.Series(new), ignore_index=True)
            self.last_secs = last_secs

    def append_secs(self, secs_tuple):
        if not secs_tuple:
            return
        d = pd.DataFrame(secs_tuple)
        d = d.set_index(d[0] * 1000000000)
        d_secs = d.set_index(pd.to_datetime(d.index))[1]
        d_min = d_secs.resample(self.get_pandas_resample_char()).mean()
        d_min = d_min.interpolate()

        last = d_min.index[-1].value / 1000000000
        self.append(d_min, last)

    def shift(self, n):
        pop = self.data[:n]
        df = pd.DataFrame(self.data)[n:]
        self.data = df.set_index(pd.Series(range(df.shape[0])))[0]
        return pop

    def get_values(self, indices):
        rl = [self.data.iloc(i) for i in indices]
        return rl


class SeriesMinute(Series):
    def get_last_max_seconds(self):
        return self.last_secs + 59

    def get_pandas_resample_char(self):
        return 'T'
