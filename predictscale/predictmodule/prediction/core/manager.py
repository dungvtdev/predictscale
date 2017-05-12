import threading
import time
from prediction.core.container import InstanceMonitorContainer


class PredictManager(threading.Thread):
    _running = False
    _loop_minute = 1
    _backend = None

    def run(self):
        while self._running:
            time.sleep(self._loop_minute * 60)

    def init_container(self, instance_meta):
        instance_id = instance_meta['instance_id']
        metric = instance_meta['metric']
        container = InstanceMonitorContainer(self._backend,
                                             instance_meta,
                                             instance_id=instance_id,
                                             metric=metric)
        return container

    def add_container(self, instance_meta):
        container = self.init_container(instance_meta)

    def start_thread(self):
        if not self.is_alive():
            self._running = True
            self.start()

    def stop_thread(self):
        self._running = False
