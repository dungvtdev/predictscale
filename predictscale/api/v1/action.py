import falcon


def enable_group_action(backend, user_id, id):
    group = backend.get_group(user_id, id)
    if group.enable:
        raise falcon.HTTPBadRequest(
            'Group currently is enable, can\'t enable again')
    else:
        group_dict = {
            'enable': True,
        }
        backend.update_groups(user_id, id, group_dict)


def disable_group_action(backend, user_id, id):
    group = backend.get_group(user_id, id)
    if not group.enable:
        raise falcon.HTTPBadRequest(
            'Group currently is disable, can\'t disable again')
    else:
        group_dict = {
            'enable': False,
        }
        backend.update_groups(user_id, id, group_dict)
