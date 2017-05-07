import requests
from . import config as cf
from . import authagent as auth
import json

client = None


class MonitorClient(object):
    endpoint = 'http://192.168.1.94:8008'

    def __init__(self):
        self.authagent = auth.UserTokenAuth(secret=cf.SECRET)

    @classmethod
    def default(cls):
        global client
        if client is None:
            client = MonitorClient()
        return client

    def get_groups(self, request):
        addr_tmpl = self.endpoint + \
            '/v1/user/{user_id}/groups'
        addr = addr_tmpl.format(user_id=1)
        r = requests.get(addr)
        if r.status_code == 200:
            groups = json.loads (r.text)['groups']
            return groups
        else:
            return []
