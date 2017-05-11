from .core.algorithm.datafeeder.exceptions import *


class DataFetchError(Exception):
    pass


class EndpointConnectionRefuse(Exception):
    pass


class EndpointNotAvailable(Exception):
    pass
