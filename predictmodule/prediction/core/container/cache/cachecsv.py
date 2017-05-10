from prediction.backend import default as backend
import pandas as pd
import os
from .. import DataMeta
from ...series import SeriesMinute
import uuid

dirname = os.path.abspath(os.path.dirname(__file__))


def get_csv_cache(instance_meta):
    id = instance_meta['instance_id']
    metric = instance_meta['metric']

    cache_meta = backend.get_cache_meta(id, metric)
    if cache_meta is None:
        return

    path = os.path.join(dirname, cache_meta['file'])
    if os.path.isfile(path):
        df = pd.read_csv(path, header=None)
        s = pd.Series(df[0])
        return DataMeta(source='cached', data=s, last=cache_meta['last'])
    else:
        backend.drop_cache_meta(cache_meta)
        return None


def cache_to_csv(instance_meta, data, last):
    id = instance_meta['instance_id']
    metric = instance_meta['metric']

    cache_meta = backend.get_cache_meta(id, metric)
    if cache_meta is not None:
        path = os.path.join(dirname, cache_meta['file'])
        series = SeriesMinute()
        series.last = cache_meta['last']
        series.append(data, last)
        pdseries = series.data
        pdseries.to_csv(path, mode='a', header=False, index=None)
        cache_meta['last'] = last
    else:
        name = uuid.uuid4()
        cache_meta = {
            'id': 0,
            'last': last,
            'file': name,
        }
        path = os.path.join(dirname, cache_meta['file'])
        data.to_csv(path, header=False, index=None)

    backend.save_cache_meta(cache_meta)
