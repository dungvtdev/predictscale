import json
from . import influxdbdriver as driver
from . import base
import time
from predictmodule import utils
import numpy as np


def container_filter(serie, name):
    return serie["tags"]["container_name"] == name


def extract_data(data, filter):
    jdata = json.loads(data)
    if jdata.get("results", None) is None \
            or not jdata["results"][0]:
        print("Get Empty data")
        return
    series = jdata["results"][0]["series"]
    values = next(s["values"] for s in series if filter(s))
    return values


def clamp_01(data):
    data[(data > 1) | (data < 0)] = np.nan
    data = data.interpolate()
    i = 0
    while(np.isnan(data[i])):
        data[i] = 0
        i = i + 1
    return data


def convert_data_minute_to_pandas(data):
    if data is None:
        return
    return utils.time_series_to_pandas_series_minute(data)


class CpuRootMixin():
    def filter(self, serie):
        return container_filter(serie, "/")

    def get_query(self, begin, end):
        if end is not None:
            q = 'SELECT derivative("value", 1s)/1000000000 FROM {metric} WHERE time >= {utc_begin}{epoch} AND time <= {utc_end}{epoch} GROUP BY "container_name" fill(null)'
        else:
            q = 'SELECT derivative("value", 1s)/1000000000 FROM {metric} WHERE time >= {utc_begin}{epoch} GROUP BY "container_name" fill(null)'
        q = q.format(utc_begin=begin, utc_end=end,
                     epoch=self._epoch, metric=self._metric)
        return q


class BaseMetricFetch(driver.DataBatchGet):
    def __init__(self, **kwargs):
        base.populate_params(self, **kwargs)

        query_service = driver.QueryData()
        query_service.setup(**kwargs)

        driver.DataBatchGet.__init__(
            self, query_service, **kwargs)

    def extract_data(self, data):
        filter = self.filter or (lambda d: True)
        d = extract_data(data, filter)
        if d is None:
            raise Exception('Get data None')
        last = d[-1][0]
        return convert_data_minute_to_pandas(d), last

    def extend_data(self, current, new):
        if current is None:
            return new
        if new is not None:
            rl = new.append(current)
            del current
            del new
            return rl
        return current


class CpuFetch(CpuRootMixin, BaseMetricFetch):
    def get_short_data_as_list(self, begin):
        begin = int(begin)
        q = self.get_query(begin, None)
        rl = self.query_service.query_data(q)
        data, last = self.extract_data(rl)
        data = clamp_01(data)
        return data.tolist(), last

    def extract_data(self, data):
        d, last = BaseMetricFetch.extract_data(self, data)
        return clamp_01(d), last


class DiscoverLastTimeMinute():
    def __init__(self, **kwargs):
        base.populate_params(self, **kwargs)
        query_service = driver.QueryData()
        query_service.setup(**kwargs)
        self.query_service = query_service

    def get_query(self):
        epoch = self._epoch if self._epoch != 's' else 'm'
        q_tmpl = 'select * from {metric} where time > now() - 2{epoch} group by * order by desc limit 1'
        q = q_tmpl.format(metric=self._metric, epoch=self._epoch)
        return q

    def filter(self, serie):
        return container_filter(serie, "/")

    def __call__(self, *args):
        q = self.get_query()
        pydata = self.query_service.query_data(q)
        data = extract_data(pydata, self.filter)
        if data:
            return data[0][0]


class DiscoverBeginTimeMinute(DiscoverLastTimeMinute):
    def get_query(self):
        epoch = self._epoch if self._epoch != 's' else 'm'
        q_tmpl = 'select * from {metric} where time >= {utc_begin}{epoch} group by * order by asc limit 1'
        q = q_tmpl.format(metric=self._metric,
                          epoch=self._epoch, utc_begin=self._begin)
        return q

    def __call__(self, begin):
        self._begin = begin
        return DiscoverLastTimeMinute.__call__(self, begin)
