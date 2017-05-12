from . import prediction as prd


def get_instance_data_info(instance_meta):
    container = manager.init_container(instance_meta)
    msg = container.get_data_info_string()
    return msg
