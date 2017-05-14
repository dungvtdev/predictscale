    from share import configtool
from share import baseconfig
from share import log
import config

if __name__ == '__main__':
    configtool.apply_all_config(baseconfig)
    configtool.apply_all_config(config)
    log.init(configtool)

    from predictmodule.manager import PredictManager
    manager = PredictManager.default()
    manager.start_thread()

    from app import App

    server = App(configtool)

    server.listen()

    manager.stop_thread()
