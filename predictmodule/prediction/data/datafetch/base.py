class FetchMixin():
    def __init__(self, **kwargs):
        self._endpoint = kwargs.get('endpoint')
        self._db_name = kwargs.get('db_name')
        self._batch_size = kwargs.get('batch_size', None)
        self._epoch = kwargs.get('epoch', None)
        self._metric = kwargs.get('metric', None)
