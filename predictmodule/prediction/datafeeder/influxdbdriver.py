import requests
import json


class QueryData():

    def __init__(self):
        self.url = None
        self.url_tmpl = "http://{endpoint}/query"
        self.params = {
            'db': 'cadvisor',
            'epoch': 's',
            'q': None
        }

    def setup(self, endpoint=None, db=None, **kwargs):
        self.params['db'] = db or self.params['db']
        self.url = self.url_tmpl.format(endpoint=endpoint)

    def query_data(self, query):
        self.params['q'] = query
        r = requests.get(self.url, self.params)
        if r.status_code == 200:
            return r.text
        else:
            raise Exception('Query error')


class DataBatchGet():

    def __init__(self, query_service, batch_size):
        self.query_service = query_service
        self.batch_size = batch_size

    def get_data(self, utc_begin, utc_end):
        try:
            utc_begin = int(utc_begin)
            utc_end = int(utc_end)
            last = utc_begin
            result = None
            while last < utc_end:
                begin = last
                last = last + self.batch_size
                last = utc_end if last > utc_end else last
                q = self.get_query(begin, last)
                rl = self.query_service.query_data(q)
                exdata = self.extract_data(rl)
                if not result:
                    result = exdata
                else:
                    result.extend(exdata)
            print('Get Success')
            return result
        except:
            print('Error')

    def get_query(self, utc_begin, utc_end):
        raise NotImplementedError('get_query must be implement')

    def extract_data(self, data):
        raise NotImplementedError('extract_data must be implement')
