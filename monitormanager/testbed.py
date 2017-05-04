import falcon
from wsgiref import simple_server

api = falcon.API()
app = application = api


class Resource(object):
    def on_post(self, req, resp):
        print('post')

    def on_put(self, req, resp, test_id):
        print(test_id)

app.add_route('/test', Resource())
app.add_route('/test/{test_id}', Resource())

httpd = simple_server.make_server('127.0.0.1', 8000, app)
httpd.serve_forever()
