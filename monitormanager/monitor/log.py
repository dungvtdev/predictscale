import os
import logging


def init(config_module):
    global def_config
    def_config = config_module.get_config('LOG')


def get_params(config):
    file = config.get('file', None)
    level_s = config.get('level', None)

    if not file or not level_s:
        raise ValueError('file, level of log must be defined \
        file: %s, level: %s' % (file, level_s))

    level = getattr(logging, level_s)

    # create folder file
    directory = os.path.dirname(file)
    if directory and not os.path.exists(directory):
        os.mkdir(directory)

    handler = logging.FileHandler(file)
    handler.setLevel(level)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    return level, handler


def get_log(name, config=None):
    global def_config

    config = config or def_config
    level, handler = get_params(config)

    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)

    return logger
