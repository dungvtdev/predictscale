import pandas as pd


class Series(object):
    name = ''
    last = None
    data = None

    def get_last_in_second(self):
        raise NotImplementedError('get_lasst_in_second must be implement')

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

    def append_secs(self, secs_tuple):
        d = pd.DataFrame(secs_tuple)
        d = d.set_index(d[0] * 1000000000)
        d_secs = d.set_index(d.index.to_datetime())[1]
        d_min = d_secs.resample(self.get_pandas_resample_char(),
                                how='mean')
        self.append(d_min, d_min.index[-1])


class SeriesMinute(Series):
    def get_last_in_second(self):
        return (last + 1) * 60 - 1

    def get_pandas_resample_char(self):
        return 'T'
