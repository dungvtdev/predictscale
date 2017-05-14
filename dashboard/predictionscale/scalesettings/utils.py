from openstack_dashboard.dashboards.predictionscale.backend \
    import client


def drop_group(request, group_id):
    client(request).drop_group(group_id)


def create_group(request, group):
    return client(request).add_group(group)


def enable_group(request, id):
    return client(request).enable_group(id)


def disable_group(request, id):
    return client(request).disable_group(id)


def get_data_state(request, id, *args):
    return client(request).get_data_state(id, *args)


def run_group(request, id, params):
    return client(request).run_group(id, params)
