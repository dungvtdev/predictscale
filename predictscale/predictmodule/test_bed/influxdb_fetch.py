import startup
from prediction.core.datafetch import influxdb

params = {
    "batch_size": 1000,
    "endpoint": '192.168.122.124',
    "db_name": 'cadvisor',
    'epoch': 'm',
    'metric': 'cpu_usage_total'
}

# test cputotalfetch

utc_b = 1494333260/60 - 2000/60
utc_e = 1494333260/60

cpu_fetch = influxdb.CPUFetch(**params)
rl = cpu_fetch.get_data(utc_b, utc_e)
print(rl[:4])
print(len(rl))


# test discover last time
discover = influxdb.DiscoverLastTime(**params)
rl = discover()
print(rl)
