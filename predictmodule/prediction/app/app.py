import threading


class Application(threading.Thread):
    predictor_manager = None

    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        predictor_manager = kwargs.get('predictor_manager', None)

    def run(self):
        # check new container
        self.predictor_manager.update_finish_container()

        # fetch all data tick

    def _fetch_new_data(self):
        pass

    def create_predictor(self, instance_id):
        self.predictor_manager.create_predictor(instance_id)

    def check_predictor_status(self, instance_id):
        self.predictor_manager.check_predictor_status(instance_id)

    def predict(self, instance_id, new_data):
        return self.predictor_manager.predict(instance_id, new_data)

    def discovery_data(self, meta):
        pass

    def get_data_to_train(self):
        pass
