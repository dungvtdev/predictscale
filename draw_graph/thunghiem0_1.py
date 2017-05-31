import requests
import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt

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


def calc_accurency(arr_true, arr_predict, chunks, func):
    rl = []
    for ch in chunks:
        arr_true_c = arr_true[(arr_true.index >= ch[0]) & (arr_true.index < ch[1])]
        arr_predict_c = arr_predict[(arr_predict.index >= ch[0]) & (arr_predict.index < ch[1])]
        rl.append(func(arr_true_c, arr_predict_c))
    return rl


if __name__ == '__main__':
    begin = '2017-05-27 7:27:00'
    end = '2017-05-27 11:04:00'

    ax = plt.subplot()
    ax.set_color_cycle(['blue', 'red', 'green'])

    data = get_data(begin, end)
    data_d = json.loads(data)['results'][0]['series']

    real = next((it for it in data_d if it['tags']['type'] == 'real'), None)
    real = real['values']
    real_convert = convert_to_dataframe(real)
    # real_convert = real_convert.resample('T').mean()
    ax.plot(real_convert.index, real_convert[0], label='Real', zorder=1)

    predict = next((it for it in data_d if it['tags']['type'] == 'predict'), None)
    predict = predict['values']
    predict_convert = convert_to_dataframe(predict)
    ax.plot(predict_convert.index, predict_convert[0], '--', label='Predict', zorder=2)

    scale_up_data = get_data_scale(begin, end, "scale_up")
    scale_up_d = json.loads(scale_up_data)['results'][0]['series'][0]["values"]
    scale_up_convert = convert_to_dataframe(scale_up_d)
    # predict_convert = predict_convert.resample('T').mean()
    ax.scatter(scale_up_convert.index, scale_up_convert[0], marker='^', s=100, c='black', label='Node Up', zorder=3)

    scale_down_data = get_data_scale(begin, end, "scale_down")
    scale_down_d = json.loads(scale_down_data)['results'][0]['series'][0]["values"]
    scale_down_convert = convert_to_dataframe(scale_down_d)
    ax.scatter(scale_down_convert.index, scale_down_convert[0], marker='s', s=100, c='black', label='Node Down',
               zorder=4)

    # lay cac doan
    rl = []
    for i in range(scale_down_convert.shape[0] + scale_up_convert.shape[0] - 1):
        if i % 2 == 0:
            idx = i / 2
            rl.append((scale_up_convert.index[idx], scale_down_convert.index[idx]))
        else:
            idx = (i - 1) / 2
            rl.append((scale_down_convert.index[idx], scale_up_convert.index[idx + 1]))

    # lay data tung khoang
    mae = calc_accurency(real_convert, predict_convert, rl, mean_absolute_error)
    rmse = calc_accurency(real_convert, predict_convert, rl, lambda x, y: sqrt(mean_squared_error(x, y)))

    print(mae)
    print(rmse)
    # plt.show()
