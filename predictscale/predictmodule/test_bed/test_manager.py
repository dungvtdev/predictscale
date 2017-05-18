import startup
from share import configtool
from share import baseconfig
from share import log
import config

# manager = PredictManager()
# manager.start_thread()
# # time.sleep(3)
# manager.stop_thread()

instance_meta = {
    'instance_id': 1,
    'period': 10,
    'data_length': 60,
    'predict_length': 10,
    'update_in_time': 10,
    'endpoint': '192.168.122.124',
    'db_name': 'cadvisor',
    'neural_size': 15,
    'recent_point': 4,
    'periodic_number': 1,
    'metric': 'cpu_usage_total',
}

instance_meta['epoch'] = 'm'

configtool.apply_all_config(baseconfig)
configtool.apply_all_config(config)
log.init(configtool)

import startup
import time
from predictmodule.manager import PredictManager, create_container

# container = create_container(instance_meta)
# msg = container.get_data_info_string()
# print(msg)

# container.push()

manager = PredictManager.default()

manager.start_thread()

manager.update_container(instance_meta)
# container = create_container(instance_meta)
# container.setup_wait()

time.sleep(50 * 60)

manager.stop_thread()
