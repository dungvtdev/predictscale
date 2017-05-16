import falcon
from .backend import DBBackend
from . import action
import re
from predictmodule import apiutils


def camelcase_to_underscore(key):
    return re.sub(r'([a-z])([A-Z])', r'\1_\2', key).lower()


class InstanceActionResource(object):
    db_backend = DBBackend.default()

    def on_get(self, req, resp, user_id):
        data_length = req.get_param('data_length') or None

        group_dicts = self.db_backend.get_groups(user_id)
        req.context['result'] = {
            'groups': group_dicts
        }
        # print(group_dicts)

    def on_post(self, req, resp, user_id):
        body = req.context['doc']
        # print('body')
        # print(body)
        if 'groups' not in body:
            raise falcon.HTTP_BAD_REQUEST(
                "Create group must have 'group' in body")

        self.db_backend.add_group(user_id, body['groups'])


class GroupActionResource(object):
    db_backend = DBBackend.default()

    post_map = ['run_group', 'stop_group', ]
    get_map = ['poll_process_data', ]

    def on_post(self, req, resp, user_id, id, action):
        if action in self.post_map:
            fn = getattr(self, '_{action}_action'.format(action=action))
            fn(req, resp, user_id, id)
        else:
            raise falcon.HTTPBadRequest('Method post not allow')

    def on_get(self, req, resp, user_id, id, action):
        if action in self.get_map:
            fn = getattr(self, '_{action}_action'.format(action=action))
            fn(req, resp, user_id, id)
        else:
            raise falcon.HTTPBadRequest('Method get not allow')

    def _run_group_action(self, req, resp, user_id, id):
        body = req.context['doc']
        # convert to competition key
        params = {}
        for k, v in body.items():
            k = camelcase_to_underscore(k)
            params[k] = v

        # print(params)
        # try:
        action.run_group(user_id, id, params)
        action.enable_group_action(self.db_backend, user_id, id)

        # except:
        #     raise falcon.HTTPBadRequest('Group can\'t up')

    def _stop_group_action(self, req, resp, user_id, id):
        action.stop_group(user_id, id)

    def _poll_process_data_action(self, req, resp, user_id, id):
        insts = self.db_backend.get_instances_in_group(user_id, id)
        # metric = self.db_backend.get_group(user_id, id)['metric']
        result = []
        if insts is not None:
            if not isinstance(insts, list):
                insts = [insts, ]
            for inst in insts:
                metric = 'cpu_usage_total'
                status_object = apiutils.get_instance_status(
                    inst.instance_id, metric)
                process = status_object['process']
                status = status_object['status']
                next_secs = 0
                if status == 'pushing':
                    next_secs = 2
                else:
                    next_secs = 30
                rl = {
                    'instance_id': inst.instance_id,
                    'process': process,
                    'message': status_object['message'],
                    'status': status,
                    'next_secs': next_secs,
                }
                result.append(rl)

        req.context['result'] = {
            'process': result
        }


routes = [
    ('/users/{user_id}/groups/{id}/{action}', GroupActionResource())
    # ('/users/{user_id}/instances/{id}/{action}', InstanceActionResource()),
]

# action = run_group, poll_process_data, stop_group
