from monitor import configtool
from monitor import baseconfig
from monitor import log

configtool.apply_all_config(baseconfig)
log.init(configtool)

logger = log.get_log(__name__)

logger.info("test")
