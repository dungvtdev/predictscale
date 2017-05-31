import requests
import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import datetime

endpoint = 'localhost:8086'
db_name = 'predict_result'


def get_data(begin, end):
    url = 'http://{endpoint}/query'.format(endpoint=endpoint)

    # time_filter = 'time > now() - {begin}s AND time < now() - {end}s'
    time_filter = "time > '{begin}' AND time < '{end}'".format(begin=begin, end=end)
    q = 'SELECT "value" FROM "cpu_usage_total" WHERE {time_filter} GROUP BY "type" fill(null)'.format(
        time_filter=time_filter)

    payload = {
        'db': db_name,
        'q': q,
    }

    r = requests.get(url, params=payload)
    return r.text


def get_data_scale(begin, end, name):
    url = 'http://{endpoint}/query'.format(endpoint=endpoint)

    # time_filter = 'time > now() - {begin}s AND time < now() - {end}s'
    time_filter = "time > '{begin}' AND time < '{end}'".format(begin=begin, end=end)
    q = 'select value from {name} where {time_filter} group by id'.format(
        time_filter=time_filter, name=name)

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
    begin = '2017-05-30 14:20:32'
    end = '2017-05-30 21:18:16'

    ax = plt.subplot()
    ax.set_color_cycle(['blue', 'red', 'green'])

    data = get_data(begin, end)
    data_d = json.loads(data)['results'][0]['series']

    real = next((it for it in data_d if it['tags']['type'] == 'real'), None)
    real = real['values']
    real_convert = convert_to_dataframe(real)
    # real_convert = real_convert.resample('T').mean()
    ax.plot(real_convert.index, real_convert[0], label='Real', zorder=1)

    predict = next((it for it in data_d if it['tags']['type'] == 'predict_future_0'), None)
    predict = predict['values']
    predict_convert = convert_to_dataframe(predict)
    ax.plot(predict_convert.index, predict_convert[0], '--', label='Predict', zorder=2)

    scale_up_data = get_data_scale(begin, end, "scale_up")
    scale_up_d = json.loads(scale_up_data)['results'][0]['series'][0]["values"]
    scale_up_convert = convert_to_dataframe(scale_up_d)
    # predict_convert = predict_convert.resample('T').mean()
    ax.scatter(scale_up_convert.index, scale_up_convert[0], marker='^', s=100,c='black', label='Node Up', zorder=3)

    # scale_down_data = get_data_scale(begin, end, "scale_down")
    # scale_down_d = json.loads(scale_down_data)['results'][0]['series'][0]["values"]
    # scale_down_convert = convert_to_dataframe(scale_down_d)
    # ax.scatter(scale_down_convert.index, scale_down_convert[0], marker='s', s=100,c='black', label='Node Down', zorder=4)

    plt.show()
