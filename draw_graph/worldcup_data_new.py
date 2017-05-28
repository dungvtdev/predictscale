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
    q = 'SELECT derivative("value", 1s)/1000000000 FROM "cpu_usage_total" WHERE {time_filter} GROUP BY container_name fill(null)' \
        .format(time_filter=time_filter)
    payload = {
        'db': db_name,
        'q': q,
    }

    r = requests.get(url, params=payload)
    return r.text


if __name__ == '__main__':
    begin = '2017-05-26 08:00:00'
    end = '2017-05-26 14:00:00'

    ax = plt.subplot()
    ax.set_color_cycle(['blue', 'red', 'green'])

    data = get_data(begin, end)
    data_d = json.loads(data)['results'][0]['series']

    data_total = next((it for it in data_d if it['tags']['container_name'] == '/'), None)
    data_total = data_total['values']
    data_total_df = pd.DataFrame(data_total)
    data_total_array = np.asarray(data_total_df[1])
    data_total_time = pd.to_datetime(data_total_df[0], format='%Y-%m-%d %H:%M:%S')
    data_total_convert = pd.DataFrame(data_total_array, index=data_total_time)
    data_total_convert = data_total_convert.resample('T').mean()
    ax.plot(data_total_convert.index, data_total_convert[0], label='Data')
    plt.show()
