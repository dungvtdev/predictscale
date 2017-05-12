import requests
from . import config as cf
from . import authagent as auth
import json
from .authagent import UserTokenAuth

from .models import GroupData
from . import horizonutils as utils


class Client(object):
    endpoint = 'http://192.168.1.94:8008'

    def __init__(self, user_id=None):
        self.authagent = auth.UserTokenAuth(secret=cf.SECRET)
        self.user_id = user_id

    def __call__(self, request_obj):
        self.request_obj = request_obj
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
        try:
            r = fn(url, params=params, data=json.dumps(data), headers=headers)
            return r, r.status_code == 200
        except requests.ConnectionError as e:
            print(e.message)
            raise

    def request_get(self, url, **kwargs):
        return self.request('get', url, **kwargs)

    def request_delete(self, url, **kwargs):
        return self.request('delete', url, **kwargs)

    def request_post(self, url, **kwargs):
        return self.request('post', url, **kwargs)

    def get_url(self, url_templ, **kwargs):
        kwargs['user_id'] = self.user_id or ''
        s = self.endpoint + \
            url_templ.format(**kwargs)
        return s

    def get_groups(self):
        addr_tmpl = '/v1/users/{user_id}/groups'
        url = self.get_url(addr_tmpl)
        r, ok = self.request_get(url)
        if ok:
            group_dicts = json.loads(r.text)['groups']
            groups = [GroupData.create(g) for g in group_dicts]
            return groups
        else:
            return []

    def get_group(self, group_id):
        addr_tmpl = '/v1/users/{user_id}/groups/{group_id}'
        url = self.get_url(addr_tmpl, group_id=group_id)
        r, ok = self.request_get(url)
        if ok:
            group_dicts = json.loads(r.text)['groups']
            group = GroupData(group_dicts[0])
            return group

    def drop_group(self, id):
        addr_tmpl = '/v1/users/{user_id}/groups/{id}'
        url = self.get_url(addr_tmpl, id=id)
        r, ok = self.request_delete(url)
        return ok

    def add_group(self, group):
        ips = utils.get_instances_ip(self.request_obj, group.instances)
        addr_tmpl = '/v1/users/{user_id}/groups'
        url = self.get_url(addr_tmpl)
        inst_data = zip(group.instances, ips)
        group_dict = group.to_dict()
        group_dict['instances'] = inst_data
        payload = {
            'groups': [group_dict, ]
        }
        r, ok = self.request_post(url, data=payload)
        print('************************************ add_group ***************')
        print(ips)
        print(payload)
        return ok

    def pings(self):
        url = self.get_url('/v1/users/{user_id}/pings')
        print('*****************************************')
        print(url)
        r = self.request_get(url)
        return r.text

    def enable_group(self, id):
        print('*****************************************')
        print('enable group')
        addr_tmpl = '/v1/users/{user_id}/groups/{id}/actions/enable'
        url = self.get_url(addr_tmpl, id=id)
        r, ok = self.request_post(url)
        return ok

    def disable_group(self, id):
        print('*****************************************')
        print('enable group')
        addr_tmpl = '/v1/users/{user_id}/groups/{id}/actions/disable'
        url = self.get_url(addr_tmpl, id=id)
        r, ok = self.request_post(url)
        return ok
