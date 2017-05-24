import requests
import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np

endpoint = 'localhost:8086'
db_name = 'predict_result'


def get_data(begin, end):
    url = 'http://{endpoint}/query'.format(endpoint=endpoint)

    # time_filter = 'time > now() - {begin}s AND time < now() - {end}s'
    time_filter = "time > '{begin}' AND time < '{end}'".format(begin=begin, end=end)
    q = 'SELECT "value" FROM "cpu_usage_total" WHERE {time_filter} GROUP BY "type" fill(null)' \
        .format(time_filter=time_filter)
    payload = {
        'db': db_name,
        'q': q,
    }

    r = requests.get(url, params=payload)
    return r.text


if __name__ == '__main__':
    begin = '2017-05-23 09:30:00'
    end = '2017-05-23 15:30:00'
    data = get_data(begin, end)
    series = json.loads(data)['results'][0]['series']

    real_series = next((s for s in series if s['tags']['type'] == 'real'), None)['values']
    real_series_df = pd.DataFrame(real_series)
    real_array = np.asarray(real_series_df[1])

    predict_series = next((s for s in series if s['tags']['type'] == 'predict'), None)['values']
    predict_series_df = pd.DataFrame(predict_series)
    predict_array = np.asarray(predict_series_df[1])

    mean_series = next((s for s in series if s['tags']['type'] == 'mean'), None)['values']
    mean_series_df = pd.DataFrame(mean_series)
    mean_array = np.asarray(mean_series_df[1])

    max_series = next((s for s in series if s['tags']['type'] == 'max'), None)['values']
    max_series_df = pd.DataFrame(max_series)
    max_array = np.asarray(max_series_df[1])

    ax = plt.subplot()
    ax.set_color_cycle(['red', 'blue'])
    ax.plot(real_array, label='Real')
    ax.plot(max_array, '--', label='Mean')
    ax.legend()
    plt.show()
