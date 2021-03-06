import requests
import json
from predictmodule import exceptions as ex

import re
from share import log

logger = log.get_log(__name__)


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


class DataGetBase():
    def __init__(self, query_service, **kwargs):
        self.query_service = query_service


class DataBatchGet(DataGetBase):
    def __init__(self, query_service, batch_size, **kwargs):
        self.query_service = query_service
        self.batch_size = batch_size

    def get_query(self, **kwargs):
        raise NotImplementedError('get_query must be implement')

    def extract_data(self, data):
        # return data_series, last
        raise NotImplementedError('extract_data must be implement')

    def extend_data(self, current, new):
        raise NotImplementedError('extend_data must be implement')

    def get_data(self, begin, end, filter=None, **kwargs):
        # print('Get data from %s to %s' % (begin, end))

        _begin = end
        _end = end
        result = None
        batch_size = batch_size_by_time_dv(self.batch_size, self._epoch)
        count = 0

        finish = False
        has_more = False
        while _begin > begin:
            _end = _begin
            _begin = _end - batch_size
            if _begin < begin:
                _begin = begin

            q = self.get_query(begin=_begin, end=_end, **kwargs)
            rl = self.query_service.query_data(q)
            exdata, exbegin, exlast = self.extract_data(rl)
            # print('%s %s %s' % (_begin, _end,
            #                     len(exdata) if exdata is not None else 0))
            if exdata is None:
                if _end - begin < batch_size:
                    # truong hop nay du tang batch size nua thi cung khong lay dc data,
                    # vi vong lap nay da qua begin roi
                    pass
                else:
                    batch_size = batch_size * 2
                    _begin = _end
                    continue

            if filter:
                fdata, finish = filter(exdata)
                result = self.extend_data(result, fdata)
                if finish:
                    break
            else:
                result = self.extend_data(result, exdata)
            count = count + 1
            if exbegin > _begin:
                break

        # print('Get Success %s' % count)
        logger.debug(
            'Get traning data info begin %s, last %s, count %s' % (begin, end, count))
        return result
