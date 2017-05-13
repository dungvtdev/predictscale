from predictmodule.prediction.data.datafetch import CpuFetch

instance_meta_default = {
    'recent_point': 4,
    'periodic_number': 1,
    'period': 0,
    'neural_size': 15,
    'cross_rate': 0.6,
    'mutation_rate': 0.04,
    'pop_size': 50
}

map_fetch_cls = {
    'cpu_usage_total': CpuFetch,
}

cache_root = '/home/dungvt/cache'
