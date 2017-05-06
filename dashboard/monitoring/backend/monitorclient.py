import requests
from . import config as cf
from . import authagent as auth


class MonitorClient(object):
    def __init__(self):
        self.authagent = auth.UserTokenAuth(secret=cf.SECRET)

    def get_groups(self, request):
        pass
