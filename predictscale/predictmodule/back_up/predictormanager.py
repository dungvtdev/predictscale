from .creation import container
import eventlet


pool = eventlet.GreenPool()


class PredictorManager(object):
    backend = None
    creator_queue = None
    predictor_dict = {}

    def __init__(self, backend=None, creator_queue=None):
        self.backend = backend
        self.creator_queue = creator_queue

    def create_predictor(self, instance_id):
        container = container.Container(instance_id)
        self.creator_queue.put(container)

    def update_finish_container(self):
        cs = self.creator_queue.pop_finishs()
        for c in cs:
            c.status = container.ContainerStatus.RUNNING
            self.predictor_dict[c.instance_id] = c

    def check_predictor_status(self, instance_id=None):
        pass

    def fetch_data(self):
        for container in \
                pool.imap(self._fetch_data, self.predictor_dict.values()):
            pass

    def _fetch_data(self, container):
        container.fetch_data()
