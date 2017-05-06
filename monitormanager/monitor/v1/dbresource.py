import falcon
from .backend import DBBackend


class GroupResource(object):
    db_backend = DBBackend.default()

    def on_get(self, req, resp, user_id):
        group_dicts = self.db_backend.get_groups(user_id)
        req.context['result'] = {
            'groups': group_dicts
        }

    def on_post(self, req, resp, user_id):
        body = req.context['doc']
        if 'group' not in body:
            raise falcon.HTTP_BAD_REQUEST(
                "Create group must have 'group' in body")

        self.db_backend.add_group(user_id, body['group'])


class GroupResourceId(object):
    db_backend = DBBackend.default()

    def on_delete(self, req, resp, user_id, group_id):
        self.db_backend.drop_group(user_id, group_id)

    def on_put(self, req, resp, user_id, group_id):
        body = req.context['doc']
        if 'group' not in body:
            raise falcon.HTTP_BAD_REQUEST(
                "Update group must have 'group' in body")
        self.db_backend.update_groups(
            user_id, group_id, body['group'])

    def on_get(self, req, resp, user_id, group_id):
        group_dict = self.db_backend.get_group(user_id, group_id)
        req.context['result'] = {
            'groups': [group_dict]
        }


routes = [
    ('/user/{user_id}/groups', GroupResource()),
    ('/user/{user_id}/groups/{group_id}', GroupResourceId())
]
