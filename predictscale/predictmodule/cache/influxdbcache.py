import requests
from share import log
import json
from predictmodule import config


class InfluxdbCache():
    _instance = None

    def __init__(self, **kwargs):
        self.endpoint = kwargs.get('endpoint', 'localhost')
        self.db_name = kwargs.get('db_name', 'predict_result')
        self.logger = log.get_log(__name__)

    @classmethod
    def default(cls):
        if InfluxdbCache._instance is None:
            cf = config.influx_cache_config
            ep = cf['endpoint']
            db_name = cf['db_name']
            InfluxdbCache._instance = InfluxdbCache(endpoint=ep, db_name=db_name)
        return InfluxdbCache._instance

    def cache(self, minute, predict_length, instance_id, metric, mean_val, max_val, real_val):
        t = minute * 60 * 1000000000
        tmpl = '{metric},id="{id}" value={value} {time}'
        real_s = tmpl.format(metric=metric, id=instance_id, value=real_val, time=t)

        t = t + predict_length / 2 * 60 * 1000000000
        mean_s = tmpl.format(metric=metric, id=instance_id, value=mean_val, time=t)
        max_s = tmpl.format(metric=metric, id=instance_id, value=max_val, time=t)
        data = '\n'.join([real_s, mean_s, max_s, ])
        self.write(data)

    def create_database(self):
        url = "http://{endpoint}:8086/query?q=CREATE DATABASE {db_name}"
        url = url.format(endpoint=self.endpoint, db_name=self.db_name)
        requests.get(url)

    def write(self, data):
        url = 'http://{endpoint}:8086/write?db={db_name}'
        url = url.format(endpoint=self.endpoint, db_name=self.db_name)
        r = requests.post(url, data=data)
        if r.status_code == 404:
            body = json.loads(r.text)
            if "database not found" in body.get("error", ""):
                self.create_database()
                return self.write(data)

        if r.status_code != 204 or r.status_code != 200:
            self.logger.error('Error write values. Status code %s' % r.status_code)
            return False
        return True
