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


if __name__ == '__main__':
    begin = '2017-05-27 7:27:00'
    end = '2017-05-27 11:04:00'

    ax = plt.subplot()
    ax.set_color_cycle(['blue', 'red', 'green'])

    data = get_data(begin, end)
    data_d = json.loads(data)['results'][0]['series']

    real = next((it for it in data_d if it['tags']['type'] == 'real'), None)
    real = real['values']
    real_df = pd.DataFrame(real)
    real_array = np.asarray(real_df[1])
    real_time = pd.to_datetime(real_df[0], format='%Y-%m-%d %H:%M:%S')
    real_convert = pd.DataFrame(real_array, index=real_time)
    # real_convert = real_convert.resample('T').mean()
    ax.plot(real_convert.index, real_convert[0], label='Real')

    predict = next((it for it in data_d if it['tags']['type'] == 'predict'), None)
    predict = predict['values']
    predict_df = pd.DataFrame(predict)
    predict_array = np.asarray(predict_df[1])
    predict_time = pd.to_datetime(predict_df[0], format='%Y-%m-%d %H:%M:%S')
    predict_convert = pd.DataFrame(predict_array, index=predict_time)
    # predict_convert = predict_convert.resample('T').mean()
    ax.plot(predict_convert.index, predict_convert[0], '--', label='Predict')

    scale_up_data = get_data_scale(begin, end, "scale_up")
    scale_up_d = json.loads(scale_up_data)['results'][0]['series'][0]["values"]
    scale_up_df = pd.DataFrame(scale_up_d)
    scale_up_array = np.asarray(scale_up_df[1])
    scale_up_time = pd.to_datetime(scale_up_df[0], format='%Y-%m-%d %H:%M:%S')
    scale_up_convert = pd.DataFrame(scale_up_array, index=scale_up_time)
    # predict_convert = predict_convert.resample('T').mean()
    ax.scatter(scale_up_convert.index, scale_up_convert[0], marker='o', s=200,c='brown', label='Node Up')

    scale_down_data = get_data_scale(begin, end, "scale_down")
    scale_down_d = json.loads(scale_down_data)['results'][0]['series'][0]["values"]
    scale_down_df = pd.DataFrame(scale_down_d)
    scale_down_array = np.asarray(scale_down_df[1])
    scale_down_time = pd.to_datetime(scale_down_df[0], format='%Y-%m-%d %H:%M:%S')
    scale_down_convert = pd.DataFrame(scale_down_array, index=scale_down_time)
    # predict_convert = predict_convert.resample('T').mean()
    ax.scatter(scale_down_convert.index, scale_down_convert[0], marker='o', s=200,c='black', label='Node Down')

    plt.show()
