from .manager import PredictManager
from . import config


def preprocess_instance_meta(instance_meta):
    default = config.instance_meta_default

    instance_meta['metric'] = 'cpu_usage_total'
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
