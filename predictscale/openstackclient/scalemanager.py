from predictmodule import config
from api.v1 import backend

class ScaleManager():
    def __init__(self, group_id):
        self._group_id = group_id
        self._duration = config.scale_settings['minute_duration']
        self._backend = backend.DBBackend.default()

    def scale(self):
