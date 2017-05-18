import falcon
from .backend import DBBackend
from .action import enable_group_action, disable_group_action
from predictmodule import apiutils


class GroupResource(object):
    db_backend = DBBackend.default()

    def on_get(self, req, resp, user_id):
        group_dicts = self.db_backend.get_groups(user_id)
        if group_dicts is not None:
            for gd in group_dicts:
                insts = gd['instances'] or []
                statuses = []
                for inst in insts:
                    statuses.append(apiutils.get_instance_status(
                        inst, 'cpu_usage_total'))
                if len(statuses) == 0:
                    gd['process'] = 'No Instances'
                else:
                    if gd['enable']:
                        count = len(
                            [i for i in statuses if i['status'] == 'running'])
                        gd['process'] = "Run %s/%s" % (count, len(statuses))
                    else:
                        gd['process'] = 'Not Active'

        # print(group_dicts)
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


class GroupResourceId(object):
    db_backend = DBBackend.default()

    def on_delete(self, req, resp, user_id, id):
        self.db_backend.drop_group(user_id, id)

    def on_put(self, req, resp, user_id, id):
        body = req.context['doc']
        if 'group' not in body:
            raise falcon.HTTP_BAD_REQUEST(
                "Update group must have 'group' in body")
        self.db_backend.update_groups(
            user_id, id, body['group'])

    def on_get(self, req, resp, user_id, id):
        group_dict = self.db_backend.get_group(user_id, id)
        req.context['result'] = {
            'groups': [group_dict, ]
        }


class GroupAction(object):
    db_backend = DBBackend.default()

    def action_enable(self, user_id, id):
        return enable_group_action(self.db_backend, user_id, id)

    def action_disable(self, user_id, id):
        return disable_group_action(self.db_backend, user_id, id)

    def on_post(self, req, resp, user_id, id, action):
        fn = getattr(self, 'action_%s' % action, None)
        if not fn:
            raise falcon.HTTPBadRequest('Can\'t handle action %s' % action)
        return fn(user_id, id)


routes = [
    ('/users/{user_id}/groups', GroupResource()),
    ('/users/{user_id}/groups/{id}', GroupResourceId()),
    # ('/users/{user_id}/groups/{id}/actions/{action}', GroupAction())
]
