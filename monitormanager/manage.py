from monitor import configtool
from monitor import baseconfig
from monitor import log
import config

from app import App

if __name__ == '__main__':
    configtool.apply_all_config(baseconfig)
    configtool.apply_all_config(config)
    log.init(configtool)

    server = App(configtool)
    server.listen()
