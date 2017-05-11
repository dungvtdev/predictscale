import startup
import time
from prediction.core import PredictManager

manager = PredictManager()
# manager.start_thread()
# # time.sleep(3)
# manager.stop_thread()

instance_meta = {
    'instance_id': 1,
    'action': {
        'period': 10,
        'n_period_to_train': 2,
        'n_predict': 3,
        'auto_retrain_period': 10,
    },
    'endpoint': '192.168.122.124',
    'db_name': 'cadvisor',
    'train_params': {
        'n_neural_hidden': 15,
        'n_input': 4,
        'n_periodic': 1,
    },
    'metric': 'cpu_usage_total',
}

data = manager.prepare_container(instance_meta)
print(data)