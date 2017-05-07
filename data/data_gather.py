import requests
import sys
import json
import time
import csv


class QueryData():
    def __init__(self, endpoint):
        self.url = "http://{endpoint}/query".format(endpoint=endpoint)
        self.params = {
            'db': 'cadvisor',
            'epoch': 's',
            'q': None
        }

    def query_data(self, query):
        self.params['q'] = query
        r = requests.get(self.url, self.params)
        if r.status_code == 200:
            return r.text
        else:
            raise Exception('Query error')


class DataFrameGet():
    def __init__(self, query_service, batch_size):
        self.query_service = query_service
        self.batch_size = batch_size

    def get_data(self, utc_begin, utc_end, out):
        try:
            csv_writer = csv.writer(out, delimiter=' ')
            print('Getting data')
            last = utc_begin
            while last < utc_end:
                begin = last
                last = last + self.batch_size
                last = utc_end if last > utc_end else last
                q = self.get_query(begin, last)
                percentage = (last - utc_begin) * 100 / (utc_end - utc_begin)
                print('Frame[{b}:{l}] {p} %'.format(
                    b=begin, l=last, p=percentage))
                rl = self.query_service.query_data(q)
                self.write_data(rl, csv_writer)
        except:
            print('Error')
        finally:
            out.close()
            print('Finish')

    def get_query(self, utc_begin, utc_end):
        q = 'SELECT derivative("value", 1s)/1000000000 FROM "cpu_usage_total" WHERE time > {utc_begin}s AND time < {utc_end}s GROUP BY "container_name" fill(null)'
        q = q.format(utc_begin=utc_begin, utc_end=utc_end)
        return q

    def write_data(self, data, out):
        jdata = json.loads(data)
        if not jdata.get("results", None):
            print("Get Empty data")
            return
        series = jdata["results"][0]["series"]
        values = next(s["values"] for s in series
                      if s["tags"]["container_name"] == "/")
        out.writerows(values)


if __name__ == '__main__':
    ep = '192.168.122.124:8086'
    batch_size = 3600
    qservice = QueryData(ep)
    data_get = DataFrameGet(qservice, batch_size)

    f = open('data.csv', 'w')

    now = int(time.time())
    amount = 1.8*3600*24

    data_get.get_data(int(now - amount), now, f)
