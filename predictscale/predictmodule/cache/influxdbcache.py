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

    def cache(self, minute, predict_length, instance_id, metric, predict_list, real_val):
        t = minute * 60 * 1000000000
        tmpl = '{metric},id="{id}",type={type} value={value} {time}'
        real_s = tmpl.format(metric=metric, id=instance_id, value=real_val, type='real', time=t)

        if predict_list:
            t = t + 60 * 1000000000
            predict_val = predict_list[0]
            predict_s = tmpl.format(metric=metric, id=instance_id, value=predict_val, type='predict', time=t)

            t = t + predict_length / 2 * 60 * 1000000000
            mean_val = sum(predict_list)/len(predict_list)
            max_val = max(predict_list)
            mean_s = tmpl.format(metric=metric, id=instance_id, value=mean_val, type='mean', time=t)
            max_s = tmpl.format(metric=metric, id=instance_id, value=max_val, type='max', time=t)
            data = '\n'.join([real_s, mean_s, max_s, predict_s])
            self.write(data)
        else:
            data = real_s
            self.write(data)

    def cache_point(self, minute, instance_id, value, name):
        t = minute * 60 * 1000000000
        tmpl = '{name},id="{id}" value={value} {time}'
        s = tmpl.format(name=name, id=instance_id, value=value, time=t)
        self.write(s)

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

        if r.status_code != 204 and r.status_code != 200:
            self.logger.error('Error write values. Status code %s' % r.status_code)
            return False

        print('cache data success')
        return True
