from predictmodule.datafetch import CpuFetch

instance_meta_default = {
    'recent_point': 4,
    'periodic_number': 1,
    'period': 0,
    'neural_size': 15,
    'cross_rate': 0.6,
    'mutation_rate': 0.04,
    'pop_size': 50,
    'metric': 'cpu_usage_total',
    'db_name': 'cadvisor',
    'epoch': 'm'
}

map_fetch_cls = {
    'cpu_usage_total': CpuFetch,
}

cache_root = '/home/dungvt/cache'

cache_temp_expire = 3600

chunk_series_length_bias = 20

cache_predict_tmpl = 'inst:{instance_id}:{metric}:predict'

user_data_init = (
    '#!/bin/bash',
    'SERVER_IP={server_ip}'
)
user_data_init = '\n'.join(user_data_init)

influx_cache_config = {
    'endpoint':'localhost',
    'db_name': 'predict_result'
}

scale_settings = {
    'minute_duration': 15,
}

minute_per_one = 4

