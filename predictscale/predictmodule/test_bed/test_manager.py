import startup
import time
from predictmodule import PredictManager, create_container


manager = PredictManager()
# manager.start_thread()
# # time.sleep(3)
# manager.stop_thread()

instance_meta = {
    'instance_id': 1,
    'period': 10,
    'data_length': 100,
    'predict_length': 3,
    'update_in_time': 10,
    'endpoint': '192.168.122.124',
    'db_name': 'cadvisor',
    'neural_size': 15,
    'recent_point': 4,
    'periodic_number': 1,
    'metric': 'cpu_usage_total',
}

instance_meta['epoch'] = 'm'

container = create_container(instance_meta)
msg = container.get_data_info_string()
print(msg)
