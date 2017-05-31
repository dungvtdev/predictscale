import falcon
from wsgiref import simple_server

from share import log
from api import middlewares
from api import v1


class App(object):
    def __init__(self, config_holder):
        self._conf = config_holder.get_config('SERVER')
        self._logger = log.get_log(__name__)

        endpoints = self._get_endpoints()
        middlewares = self._get_middlewares()

        self.app = falcon.API(middleware=middlewares)
        self.app.add_error_handler(Exception, self._error_handler)

        for ver, ep in endpoints:
            for route, res in ep:
                self.app.add_route(ver + route, res)

    def _get_endpoints(self):
        return [
            ('/v1', v1.endpoint)
        ]

    def _get_middlewares(self):
        return [
            middlewares.JwtAuth(),
            middlewares.RequireJSON(),
            middlewares.JSONTranslator(),
        ]

    def _error_handler(self, exc, request, response, params):
        """Handler error"""
        if isinstance(exc, falcon.HTTPError):
            raise exc
        self._logger.exception(exc)
        raise falcon.HTTPInternalServerError('Internal server error', exc)

    def listen(self):
        self._logger.info("*************************************"
                          "*******    Start     ****************"
                          "*************************************")
        server_conf = self._conf

        host = server_conf['address']
        port = server_conf['port']
        msgtmpl = u'Serving on host %(host)s:%(port)s'
        self._logger.info(msgtmpl, {'host': host, 'port': port})
        # print(msgtmpl % {'host': host, 'port': port})

        httpd = simple_server.make_server(host, port, self.app)
        httpd.serve_forever()
