import json
from . import influxdbdriver as driver
from . import base
import time
import pandas as pd


def container_filter(serie, name):
    return serie["tags"]["container_name"] == name


class DataMinuteMixin():

    def get_current_data_minute(self, utc=None, seconds=None):
        if hasattr(self, 'get_data'):
            utc = utc or (time.time() - seconds)
            utc_begin = utc
            utc_end = utc_begin + seconds
            return self.get_data(utc_begin, utc_end)
        else:
            raise Exception('DataMinuteMixin need object has attr get_data')

    def get_current_data_one_minute(self, utc):
        return self.get_current_data_minute(utc, 60)


class CPUFetch(base.FetchMixin, DataMinuteMixin, driver.DataBatchGet):
    # batch_size seconds
    # endpoint: ip:port

    def __init__(self, **kwargs):
        base.FetchMixin.__init__(self, **kwargs)

        query_service = driver.QueryData()
        query_service.setup(**kwargs)

        driver.DataBatchGet.__init__(self, query_service, self._batch_size)

    def get_query(self, utc_begin, utc_end):
        q = 'SELECT derivative("value", 1s)/1000000000 FROM {metric} WHERE time > {utc_begin}{epoch} AND time < {utc_end}{epoch} GROUP BY "container_name" fill(null)'
        q = q.format(utc_begin=utc_begin, utc_end=utc_end,
                     epoch=self._epoch, metric=self._metric)
        return q

    def filter(self, serie):
        return container_filter(serie, "/")

    def extract_data(self, data):
        jdata = json.loads(data)
        if jdata.get("results", None) is None \
                or not jdata["results"][0]:
            print("Get Empty data")
            return
        series = jdata["results"][0]["series"]
        values = next(s["values"] for s in series if self.filter(s))
        return values

    def extend_data(self, current, new):
        if current is None:
            rl = pd.DataFrame(new)
            del new
        else:
            rl = current.append(new)
            del new
            del current
        return rl


class DiscoverLastTime(CPUFetch):
    def get_query(self, utc_begin, utc_end):
        epoch = self._epoch if self._epoch != 's' else 'm'
        q_tmpl = 'select * from {metric} where time > now() - 1{epoch} group by * order by desc limit 1'
        q = q_tmpl.format(metric=self._metric, epoch=self._epoch)
        return q

    def extend_data(self, current, new):
        return driver.DataBatchGet.extend_data(self, current, new)

    def __call__(self):
        rl = self.get_data()
        if rl:
            return rl[0][0]
