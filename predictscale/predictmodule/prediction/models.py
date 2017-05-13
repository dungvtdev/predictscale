class DataMeta:
    instance_id = None
    metric = None
    data = None
    last_time = None

    def __init__(self, **kwargs):
        self.data = kwargs.get('data', None)
        self.last_time = kwargs.get('last_time', None)
        self.instance_id = kwargs.get('instance_id', None)
        self.metric = kwargs.get('metric', None)