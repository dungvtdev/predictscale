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
        # raise falcon.HTTPBadRequest(
        #     'Group currently is enable, can\'t enable again')
        pass
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


def _get_instance_metas(user_id, group_id, params=None):
    instances = backend.get_instances_in_group(user_id, group_id)
    if params is None:
        group = backend.get_group(user_id=user_id, id=group_id)
        # params = group.to_instance_meta()
        params = models.Group.to_instance_meta(group)

    instance_metas = []
    for inst in instances:
        c = {}
        c['instance_id'] = inst.instance_id
        c['endpoint'] = inst.endpoint
        c['db_name'] = inst.db_name
        for k, v in params.items():
            c[k] = params[k]
        instance_metas.append(c)

    return instance_metas


def run_group(user_id, group_id, params=None):
    instance_metas = _get_instance_metas(user_id, group_id, params)
    api.run_instances(instance_metas)


# def run_updated_instances(user_id, group_id, params=None):
#     instance_metas = _get_instance_metas(user_id, group_id, params)
#     metric = 'cpu_usage_total'
#     new_inst = [inst for inst in instance_metas \
#                 if api.is_instance_in(inst['instance_id'], inst['metric'])]


def stop_group(user_id, group_id):
    instances = backend.get_instances_in_group(user_id, group_id)
    for inst in instances:
        api.stop_instances(inst.instance_id)


def filter_container_success(instance_ids):
    return api.filter_container_success(instance_ids)


def update_group_instance(user_id, group_id, new_list, remove_list):
    current = _get_instance_metas(user_id, group_id)
    new_list_full = [c for c in current if c['instance_id'] in new_list]
    api.run_instances(new_list_full)

    for id in remove_list:
        api.stop_instances(id)

