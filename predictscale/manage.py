from share import configtool
from share import baseconfig
from share import log
import config

if __name__ == '__main__':
    configtool.apply_all_config(baseconfig)
    configtool.apply_all_config(config)
    log.init(configtool)

    from app import App

    server = App(configtool)
    server.listen()
