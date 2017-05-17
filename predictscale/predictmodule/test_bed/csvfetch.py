import pandas as pd
import os

base = os.path.dirname(__file__)

path = os.path.join(base, '1m.data.csv')
df = pd.read_csv(path, header=None)
series = pd.Series(df[0])
series = series.interpolate()

last = 123456789


class CsvFetch():
    def __init__(self, *args, **kwargs):
        pass

    def get_data(self, begin, end, **kwargs):
        idx1 = series.shape[0] - (last - begin + 1)
        idx2 = series.shape[0] - (last - end)
        return series[idx1:idx2]
