import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def normalize(data):
    return (data-data.min())/(data.max()-data.min())

def shift_fun(i):
    return round(i*10)

# data = pd.read_csv('1m.data.csv', header=None)
data = pd.read_csv('10min_workload.csv', header=None)[48 * 142:55*142]
data = data.apply(np.log10)
data = data.apply(np.log10)
# data = data.apply(np.log)
# data = data.apply(func)
data = normalize(data)
data = data.round(1)
data = data.set_index(data.index/10)
data = data.groupby(data.index).mean()
data = data.set_index(pd.Series(range(data.shape[0]))*60) * 40
print(data.shape[0])

# data = data.apply(shift_fun)

plt.plot(data.index, data)
plt.show()
