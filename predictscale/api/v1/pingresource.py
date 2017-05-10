class Ping(object):
    def on_get(self, req, resp, user_id):
        req.context['result'] = {
            'message': 'OK'
        }
        print('ping %s' % user_id)


routes = [
    ('/user/{user_id}/pings', Ping()),
]
