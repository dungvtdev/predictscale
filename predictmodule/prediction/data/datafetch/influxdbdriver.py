import requests
import json
from .. import exceptions as ex
import re


class QueryData():
    def_port = 8086

    def __init__(self):
        self.url = None
        self.url_tmpl = "http://{endpoint}/query"
        self.params = {
            'db': 'cadvisor',
            'epoch': 's',
            'q': None
        }

    def setup(self, endpoint=None, db=None, epoch='s', **kwargs):
        if re.match(r'[\d\.]*:\d+$', endpoint) is None:
            endpoint = "{ip}:{port}".format(ip=endpoint, port=self.def_port)

        self.params['db'] = db or self.params['db']
        self.params['epoch'] = epoch
        self.url = self.url_tmpl.format(endpoint=endpoint)

    def query_data(self, query):
        self.params['q'] = query
        r = requests.get(self.url, self.params)
        if r.status_code == 200:
            return r.text
        else:
            raise ex.DataFetchError('Request code is not 200 OK')


class DataBatchGet():

    def __init__(self, query_service, batch_size):
        self.query_service = query_service
        self.batch_size = batch_size

    def get_data(self, utc_begin=None, utc_end=None, **kwargs):
        try:
            utc_begin = int(utc_begin) if utc_begin is not None else None
            utc_end = int(utc_end) if utc_end is not None else None
            if utc_begin is not None and utc_end is not None:
                return self._get_data_chunk(utc_begin, utc_end, **kwargs)
            else:
                return self._get_simple_data(**kwargs)
        except ex.DataFetchError as e:
            print(e.message)
        except Exception as exc:
            print(exc.message)

    def _get_data_chunk(self, utc_begin, utc_end, **kwargs):
        begin = utc_begin
        last = utc_begin
        result = None
        while last < utc_end:
            begin = last
            last = last + self.batch_size
            last = utc_end if last > utc_end else last
            q = self.get_query(begin, last, **kwargs)
            rl = self.query_service.query_data(q)
            exdata = self.extract_data(rl)
            if not result:
                result = exdata
            else:
                result.extend(exdata)
        print('Get Success')
        return result

    def _get_simple_data(self, **kwargs):
        q = self.get_query(0, 0, **kwargs)
        rl = self.query_service.query_data(q)
        exdata = self.extract_data(rl)
        return exdata

    def get_query(self, utc_begin=None, utc_end=None, **kwargs):
        raise NotImplementedError('get_query must be implement')

    def extract_data(self, data):
        raise NotImplementedError('extract_data must be implement')
