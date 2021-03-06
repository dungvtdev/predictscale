from .manager import PredictManager
from . import config
from predictmodule.cache import fscache

metric_default = 'cpu_usage_total'


def preprocess_instance_meta(instance_meta):
    default = config.instance_meta_default

    instance_meta['metric'] = metric_default
    int_map = ['period', 'data_length', 'predict_length',
               'update_in_time', 'recent_point', 'neural_size',
               'periodic_number']
    for k in int_map:
        instance_meta[k] = int(instance_meta[k])
    # instance_meta['recent_point'] = int(instance_meta['recent_point'])
    # instance_meta['period'] = int(instance_meta['period'])
    # instance_meta['neural_size'] = int(instance_meta['neural_size'])
    # instance_meta['data_length'] = int(instance_meta['data_length'])

    instance_meta['db_name'] = instance_meta['db_name'] or default['db_name']
    instance_meta['epoch'] = instance_meta.get(
        'epoch', None) or default['epoch']
    return instance_meta


def run_instances(instance_metas):
    manager = PredictManager.default()
    if instance_metas is not None:
        for instance_meta in instance_metas:
            instance_meta = preprocess_instance_meta(instance_meta)
            manager.update_container(instance_meta)


def stop_instances(instance_id):
    metric = metric_default
    manager = PredictManager.default()
    manager.remove_container(instance_id, metric)


def get_instance_status(instance_id, metric=None):
    manager = PredictManager.default()
    status = manager.get_instance_status(instance_id, metric)
    return status

def filter_container_success(instance_ids):
    manager = PredictManager.default()
    return manager.filter_container_success(instance_ids)

def is_instance_in(instance_id, metric=None):
    manager = PredictManager.default()
    return manager.is_instance_in(instance_id)

def get_last_predict(instance_id, metric):
    key = config.cache_predict_tmpl.format(instance_id=instance_id, \
                                           metric=metric)
    manager = PredictManager.default()
    container, state = manager._get_instance(instance_id, metric)
    if container is not None and state == 'running':
        data = fscache.get_cached_data(key)
        return data
    else:
        return None