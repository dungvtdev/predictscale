import json
from . import influxdbdriver as driver
import time


class DataMinuteMixin():

    def get_current_data_minute(self, utc=None, seconds):
        if hasattr(self, 'get_data'):
            utc = utc or (time.time() - seconds)
            utc_begin = utc
            utc_end = utc_begin + seconds
            return self.get_data(utc_begin, utc_end)
        else:
            raise Exception('DataMinuteMixin need object has attr get_data')

    def get_current_data_one_minute(self, utc):
        return self.get_current_data_minute(utc, 60)


class CPUTotalFeeder(DataMinuteMixin, driver.DataBatchGet):
    # batch_size seconds
    # endpoint: ip:port

    def __init__(self, batch_size=None, endpoint=None, db_name=None, **kwargs):
        query_service = driver.QueryData()
        query_service.setup(endpoint, db, **kwargs)

        driver.DataBatchGet.__init__(self, query_service, batch_size)

    def get_query(self, utc_begin, utc_end):
        q = 'SELECT derivative("value", 1s)/1000000000 FROM "cpu_usage_total" WHERE time > {utc_begin}s AND time < {utc_end}s GROUP BY "container_name" fill(null)'
        q = q.format(utc_begin=utc_begin, utc_end=utc_end)
        return q

    def filter(self, serie):
        return series["tags"]["container_name"] == "/"

    def extract_data(self, data):
        jdata = json.loads(data)
        if not jdata.get("results", None):
            print("Get Empty data")
            return
        series = jdata["results"][0]["series"]
        values = next(s["values"] for s in series if self.filter(s))
        return values
