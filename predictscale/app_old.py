import falcon

from monitor import configtool
from monitor import baseconfig
from monitor import log
from wsgiref import simple_server

from monitor import middlewares

configtool.apply_all_config(baseconfig)
configtool.apply_all_config(config)

middlewares = [
    middlewares.DeserializeMiddleware(),
    middlewares.SerializeMiddleware()
]

app = application = falcon.API(middleware=middlewares)

log.init(configtool)

logger = log.get_log(__name__)

logger.info("*************************************"
            "*******    Start     ****************"
            "*************************************")

server_conf = configtool.get_config('SERVER')
httpd = simple_server.make_server(server_conf['address'],
                                  server_conf['port'], app)
httpd.serve_forever()
