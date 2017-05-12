import falcon
from .backend import DBBackend
from . import action


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


routes = [
    ('/users/{user_id}/instances/{id}/{action}', InstanceActionResource()),
]
