import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

minute_resample = 42

data = pd.read_csv('data.csv', sep=' ', header=None)
rs = data[1].groupby(data.index / minute_resample).mean()
rs[(rs > 1) | (rs < 0)] = np.nan
rs.interpolate()

rs.to_csv('1m.data.csv', index=False, header=False)
