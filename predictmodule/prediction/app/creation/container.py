class Container(object):
    status = None
    db = None

    def __init__(self, instance_id, db):
        self.instance_id = instance_id
        self.db = db

    def create(self):
        self.meta = self.db.get_instance()

    def fetch_data(self):
        pass


class ContainerStatus:
    NOTHING = 0
    PENDING = 1
    RUNNING = 2
