import falcon
import predictmodule as pdm
from . import backend as dbbackend
from .. import models
from predictmodule import apiutils as api


backend = dbbackend.DBBackend.default()


def get_instance_data_info(user_id, instance_id, *args):
    inst_meta_dict = backend.get_instance_meta_from_db(
        user_id, instance_id, models.instance_meta_pattern)

    return pdm.get_instance_data_info(inst_meta_dict)


# def get_instance_meta(user_id, instance_id):
#     inst_dict = backend.get_instance_meta_from_db(user_id, instance_id)


def enable_group_action(backend, user_id, id):
    group = backend.get_group(user_id, id)
    if group['enable']:
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


def run_group(user_id, group_id, params):
    instances = backend.get_instances_in_group(user_id, group_id)
    instance_metas = []
    for inst in instances:
        c = {}
        c['instance_id'] = inst.instance_id
        c['endpoint'] = inst.endpoint
        c['db_name'] = inst.db_name
        for k, v in params.items():
            c[k] = params[k]
        instance_metas.append(c)

    api.run_instances(instance_metas)


def stop_group(user_id, group_id):
    instances = backend.get_instances_in_group(user_id, group_id)
    for inst in instances:
        api.stop_instances(inst.instance_id)
