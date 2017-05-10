import requests
import json
from ... import exceptions as ex
import re


def batch_size_by_time_dv(batch_size, dv):
    arr = {
        's': 1,
        'm': 42,
    }
    value = batch_size / arr[dv]
    return value


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


class DataBatchGetBase():
    def __init__(self, query_service, batch_size):
        self.query_service = query_service
        self.batch_size = batch_size

    def get_query(self, utc_begin=None, utc_end=None, **kwargs):
        raise NotImplementedError('get_query must be implement')

    def extract_data(self, data):
        raise NotImplementedError('extract_data must be implement')

    def extend_data(self, current, new):
        raise NotImplementedError('extend data must be implement')

    def get_data(self, utc_begin=None, utc_end=None, **kwargs):
        raise NotImplementedError('get_data must be implement')


class DataBatchGet(DataBatchGetBase):
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
        except requests.ConnectionError as exc:
            raise ex.EndpointConnectionRefuse()

    def _get_data_chunk(self, utc_begin, utc_end, **kwargs):
        print('Get data from %s to %s' % (utc_begin, utc_end))

        begin = utc_begin
        last = utc_begin
        result = None
        batch_size = batch_size_by_time_dv(self.batch_size, self._epoch)
        count = 0

        def batch_data(result, begin, last):
            q = self.get_query(begin, last, **kwargs)
            rl = self.query_service.query_data(q)
            exdata = self.extract_data(rl)
            print('%s %s %s' % (begin, last,
                                len(exdata) if exdata is not None else 0))
            if not exdata:
                return result, False
            result = self.extend_data(result, exdata)
            return result, True

        while last < utc_end:
            begin = last
            last = last + batch_size
            last = utc_end if last > utc_end else last
            result, has_new = batch_data(result, begin, last)
            if not has_new:
                break
            count = count + 1
        if last < utc_end:
            last = utc_end
            result, _ = batch_data(result, begin, last)
        print('Get Success %s' % count)
        return result

    def _get_simple_data(self, **kwargs):
        q = self.get_query(0, 0, **kwargs)
        rl = self.query_service.query_data(q)
        exdata = self.extract_data(rl)
        return exdata

    def extend_data(self, current, new):
        if current is None:
            return new
        current.extend(new)
        del new
        return current


class DataBatchGetLazy(DataBatchGetBase):
    def get_data(self, begin, end, filter=None, **kwargs):
        print('Get data from %s to %s' % (begin, end))

        _begin = end
        _end = end
        result = None
        batch_size = batch_size_by_time_dv(self.batch_size, self._epoch)
        count = 0

        def batch_data(result, begin, last):
            q = self.get_query(begin, last, **kwargs)
            rl = self.query_service.query_data(q)
            exdata = self.extract_data(rl)
            print('%s %s %s' % (begin, last,
                                len(exdata) if exdata is not None else 0))
            if not exdata:
                return result, False, False
            finish = False
            if filter:
                fdata, finish = filter(exdata)
                result = self.extend_data(result, fdata)
            return result, finish, True

        while _begin > begin:
            _end = _begin
            _begin = _end - batch_size
            if _begin < begin:
                _begin = begin
            result, finish, has_more = batch_data(result, _begin, _end)
            if finish:
                break
            if not has_more:
                batch_size = batch_size * 2
                _begin = _end
            count = count + 1
        print('Get Success %s' % count)
        return result

    def extend_data(self, current, new):
        if current is None:
            return new
        if new is not None:
            new.extend(current)
            del current
            return new
