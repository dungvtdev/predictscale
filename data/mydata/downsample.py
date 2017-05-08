import pandas as pd

data = pd.read_csv('data.csv', header=None, sep=' ')

data = data.set_index(data[0]*1000000000)
data_secs = data.set_index(data.index.to_datetime())[1]
data_min = data_secs.resample('T', how='mean')

# data = pd.read_csv('data3.csv', header=None, sep=';')

# index = data.set_index(data[0]).index

# data_secs = data.set_index(index.to_datetime())[1]
# data_min = data_secs.resample('T', how='sum')

# data_min = data_min.interpolate()
