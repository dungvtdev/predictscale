import pandas as pd


class InMemoryFetch():
    def __init__(self, series):
        self.init_series(series)

    def init_series(self, series):
        if not isinstance(series.index, pd.DatetimeIndex):
            self._series = series
        else:
            s = pd.Series([])
            s = s.append(series, ignore_index=True)
            print(s)
            # isnull = pd.isnull(series)
            # print(isnull[isnull])
            self._series = s

    def fetch_series(self):
        return self._series
