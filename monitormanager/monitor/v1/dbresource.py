import falcon


class GroupResource(object):
    def on_get(self, req, resp):
        pass

    def on_post(self, req, resp):
        pass


class GroupResourceId(object):
    def on_delete(self, req, resp, group_id):
        pass

    def on_put(self, req, resp, group_id):
        pass

    def on_get(self, req, resp, group_id):
        pass


def setup_api(api):
    api.add_route('/groups', GroupResource())
    api.add_route('/groups/{group_id}', GroupResourceId())
