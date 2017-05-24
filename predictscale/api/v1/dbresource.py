import falcon
from .backend import DBBackend
from .action import update_group_instance, stop_group
from predictmodule import apiutils
from api import models


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
        stop_group(user_id, id)
        self.db_backend.drop_group(user_id, id)

    def on_put(self, req, resp, user_id, id):
        body = req.context['doc']
        new_group_data = body['group']
        if 'group' not in body:
            raise falcon.HTTP_BAD_REQUEST(
                "Update group must have 'group' in body")

        group = self.db_backend.get_group(user_id, id)
        # khong cho update sua enable
        new_group_data['enable'] = group['enable']
        if group['enable']:
            cur_instance_ids = group['instances']
            new_instances = new_group_data['instances']
            new_instance_ids = [it[0] for it in new_instances]
            remove_list = [inst for inst in cur_instance_ids if inst not in new_instance_ids]
            new_list = [inst for inst in new_instance_ids if inst not in cur_instance_ids]

            self.db_backend.update_groups(
                user_id, id, new_group_data)
            update_group_instance(user_id, id, new_list, remove_list)
        else:
            self.db_backend.update_groups(
                user_id, id, new_group_data )

    def on_get(self, req, resp, user_id, id):
        group_dict = self.db_backend.get_group(user_id, id)
        req.context['result'] = {
            'groups': [group_dict, ]
        }


# class GroupAction(object):
#     db_backend = DBBackend.default()
#
#     def action_enable(self, user_id, id):
#         return enable_group_action(self.db_backend, user_id, id)
#
#     def action_disable(self, user_id, id):
#         return disable_group_action(self.db_backend, user_id, id)
#
#     def on_post(self, req, resp, user_id, id, action):
#         fn = getattr(self, 'action_%s' % action, None)
#         if not fn:
#             raise falcon.HTTPBadRequest('Can\'t handle action %s' % action)
#         return fn(user_id, id)


routes = [
    ('/users/{user_id}/groups', GroupResource()),
    ('/users/{user_id}/groups/{id}', GroupResourceId()),
    # ('/users/{user_id}/groups/{id}/actions/{action}', GroupAction())
]
