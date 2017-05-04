import falcon
from . import backend

class GroupResource(object):
    def on_get(self, req, resp, user_id):
        pass

    def on_post(self, req, resp, user_id):
        pass


class GroupResourceId(object):
    def on_delete(self, req, resp, group_id):
        pass

    def on_put(self, req, resp, group_id):
        pass

    def on_get(self, req, resp, group_id):
        pass


routes = [
    ('/user/{user_id}/groups', GroupResource()),
    ('/user/{user_id}/groups/{group_id}', GroupResourceId())
]

