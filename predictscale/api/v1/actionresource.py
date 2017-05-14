import falcon
from .backend import DBBackend
from . import action
import re


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
        print(group_dicts)

    def on_post(self, req, resp, user_id):
        body = req.context['doc']
        print('body')
        print(body)
        if 'groups' not in body:
            raise falcon.HTTP_BAD_REQUEST(
                "Create group must have 'group' in body")

        self.db_backend.add_group(user_id, body['groups'])


class GroupActionResource(object):
    db_backend = DBBackend.default()

    def on_post(self, req, resp, user_id, id, action):
        fn = getattr(self, '_{action}_action'.format(action=action))
        fn(req, resp, user_id, id)

    def _run_group_action(self, req, resp, user_id, id):
        body = req.context['doc']
        # convert to competition key
        params = {}
        for k, v in body.items():
            k = camelcase_to_underscore(k)
            params[k] = v

        print(params)
        # try:
        action.run_group(user_id, id, params)
        # except:
        #     raise falcon.HTTPBadRequest('Group can\'t up')


routes = [
    ('/users/{user_id}/groups/{id}/{action}', GroupActionResource())
    # ('/users/{user_id}/instances/{id}/{action}', InstanceActionResource()),
]

# action = run_group
