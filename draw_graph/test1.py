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
    q = 'SELECT "value" FROM "cpu_usage_total" WHERE {time_filter} GROUP BY "type" fill(null)' \
        .format(time_filter=time_filter)
    payload = {
        'db': db_name,
        'q': q,
    }

    r = requests.get(url, params=payload)
    return r.text


def get_scale_point(begin, end, scale_type):
    url = 'http://{endpoint}/query'.format(endpoint=endpoint)

    # time_filter = 'time > now() - {begin}s AND time < now() - {end}s'
    time_filter = "time > '{begin}' AND time < '{end}'".format(begin=begin, end=end)
    q = 'SELECT "value" FROM "{scale_type}" WHERE {time_filter} GROUP BY "id" fill(null)' \
        .format(time_filter=time_filter, scale_type=scale_type)
    payload = {
        'db': db_name,
        'q': q,
    }

    r = requests.get(url, params=payload)
    return r.text


if __name__ == '__main__':
    ax = plt.subplot()
    ax.set_color_cycle(['blue', 'red', 'green'])
    # begin = '2017-05-23 09:30:00'
    # end = '2017-05-23 15:30:00'
    begin = '2017-05-24 11:30:00'
    end = '2017-05-25 03:20:00'
    data = get_data(begin, end)
    series = json.loads(data)['results'][0]['series']

    real_series = next((s for s in series if s['tags']['type'] == 'real'), None)['values']
    real_series_df = pd.DataFrame(real_series)
    real_array = np.asarray(real_series_df[1])
    real_datetime = pd.to_datetime(real_series_df[0], format='%Y-%m-%d %H:%M:%S')
    real_series_pd = pd.Series(real_array, index=real_datetime)
    # real_series_pd.plot(y='Real')
    ax.plot(real_datetime, real_array, label='Real')

    predict_series = next((s for s in series if s['tags']['type'] == 'predict'), None)['values']
    predict_series_df = pd.DataFrame(predict_series)
    predict_array = np.asarray(predict_series_df[1])
    predict_datetime = pd.to_datetime(predict_series_df[0], format='%Y-%m-%d %H:%M:%S')
    predict_series_pd = pd.Series(predict_array, index=predict_datetime)
    # predict_series_pd.plot(y='Predict')
    ax.plot(predict_datetime, predict_array, '--', label='Predict')

    mean_series = next((s for s in series if s['tags']['type'] == 'mean'), None)['values']
    mean_series_df = pd.DataFrame(mean_series)
    mean_array = np.asarray(mean_series_df[1])

    max_series = next((s for s in series if s['tags']['type'] == 'max'), None)['values']
    max_series_df = pd.DataFrame(max_series)
    max_array = np.asarray(max_series_df[1])
    max_datetime = pd.to_datetime(max_series_df[0], format='%Y-%m-%d %H:%M:%S')
    max_series_pd = pd.Series(max_array, index=max_datetime)
    # max_series_pd.plot()

    scale_point_data_up = get_scale_point(begin, end, "scale_up")
    scale_point_up = json.loads(scale_point_data_up)['results'][0]['series'][0]['values']
    scale_point_up_df = pd.DataFrame(scale_point_up)
    scale_point_array = np.asarray(scale_point_up_df[1])
    scale_point_dates = pd.to_datetime(scale_point_up_df[0], format='%Y-%m-%d %H:%M:%S')
    ax.plot(scale_point_dates, scale_point_array, 'go', markersize=18)
    # ax = plt.subplot()
    # ax.set_color_cycle(['red', 'blue'])
    # ax.plot(real_array, label='Real')
    # ax.plot(predict_array, '--', label='Predict')
    # ax.legend()
    plt.show()
