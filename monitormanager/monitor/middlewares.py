from monitor import utils

class DeserializeMiddleware(object):

    def __init__(self):
        super(DeserializeMiddleware, self).__init__()

    def _deserialize(self, req):
        deserializer = utils.JSONRequestDeserializer()
        body = deserializer.default(req)
        cloud = body['body']['cloud']
        req.env['calplus.cloud'] = str(cloud)

    def process_request(self, req, resp):
        self._deserialize(req)


class SerializeMiddleware(object):

    def __init__(self):
        super(SerializeMiddleware, self).__init__()

    def _serialize(self, resp, result):
        serializer = utils.JSONResponseSerializer()
        serializer.default(resp, result)

    def process_response(self, req, resp, resource):
        self._serialize(resp, resp.body)
