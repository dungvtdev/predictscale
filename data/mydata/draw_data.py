import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv('1m.data.csv', header=None)
plt.scatter(data.index, data)
plt.show()
