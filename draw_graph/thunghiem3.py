import requests
import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import datetime

endpoint = '192.168.122.188:8086'
db_name = 'cadvisor'


def get_data(begin, end):
    url = 'http://{endpoint}/query'.format(endpoint=endpoint)

    # time_filter = 'time > now() - {begin}s AND time < now() - {end}s'
    time_filter = "time > '{begin}' AND time < '{end}'".format(begin=begin, end=end)
    q = 'SELECT derivative("value", 1s)/1000000000 FROM "cpu_usage_total" WHERE {time_filter} GROUP BY container_name fill(null)'.format(
        time_filter=time_filter)

    payload = {
        'db': db_name,
        'q': q,
    }

    r = requests.get(url, params=payload)
    return r.text

def convert_to_dataframe(values):
    df = pd.DataFrame(values)
    array = np.asarray(df[1])
    time = pd.to_datetime(df[0], format='%Y-%m-%d %H:%M:%S')
    convert = pd.DataFrame(array, index=time)
    return convert

if __name__ == '__main__':
    begin = '2017-05-26 7:58:38'
    end = '2017-05-26 14:42:00'

    ax = plt.subplot()

    data = get_data(begin, end)
    data_d = json.loads(data)['results'][0]['series']

    real = next((it for it in data_d if it['tags']['container_name'] == '/'), None)['values']
    real_df = convert_to_dataframe(real)
    real_df = real_df.resample('T').mean()

    real_df.to_csv('data_vm.csv', header=False, index=False)

    ax.plot(real_df.index, real_df[0], label='Real')

    plt.show()