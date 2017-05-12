import falcon
import predictmodule as pdm
from . import backend
from .. import models


def get_instance_data_info(user_id, instance_id, *args):
    inst_meta_dict = backend.get_instance_meta_from_db(
        user_id, instance_id, models.instance_meta_pattern)

    return pdm.get_instance_data_info(inst_meta_dict)


def get_instance_meta(user_id, instance_id):
    inst_dict = backend.get_instance_meta_from_db(user_id, instance_id)


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
