import requests
from . import config as cf
from . import authagent as auth
import json
from .authagent import UserTokenAuth


class Client(object):
    endpoint = 'http://192.168.1.94:8008'

    def __init__(self, user_id=None):
        self.authagent = auth.UserTokenAuth(secret=cf.SECRET)
        self.user_id = user_id

    def __call__(self, request_obj):
        self.user_id = request_obj.user.id
        self.authagent.user_id = self.user_id
        return self

    def request(self, method, url, params=None, data=None, headers=None):
        fn = getattr(requests, method)
        if not headers:
            headers = {}
        self.authagent.add_token(headers)
        headers['Content-type'] = 'application/json'
        headers['Accept'] = 'application/json'
        return fn(url, params=params, data=data, headers=headers)

    def request_get(self, url, **kwargs):
        return self.request('get', url, **kwargs)

    def get_url(self, url_templ, **kwargs):
        kwargs['user_id'] = self.user_id or ''
        s = self.endpoint + \
            url_templ.format(**kwargs)
        return s

    def get_groups(self):
        addr_tmpl = self.endpoint + \
            '/v1/user/{user_id}/groups'
        addr = addr_tmpl.format(user_id=1)
        r = self.request_get(addr)
        if r.status_code == 200:
            groups = json.loads(r.text)['groups']
            return groups
        else:
            return []

    def pings(self):
        url = self.get_url('/v1/user/{user_id}/pings')
        print('*****************************************')
        print(url)
        r = self.request_get(url)
        return r.text
