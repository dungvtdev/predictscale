'''
instance:{
    instance_id,
    action:{
        period : so phut,
        n_period_to_train: so lan period bat dau train,
        n_predict: so diem (phut) dc predic,
        auto_retrain_period: so phut train lai network
    },
    train_params,
    endpoint,
    db_name
}
'''


class DataBackend(object):
    def get_instance_meta(self, instance_id, metric):
        pass

    def get_cache_meta(self, instance_id, metric):
        return {
            'id': 0,
            'last': 0,
            'file': '',
        }

    def drop_cache_meta(self, cache_meta):
        pass

    def save_cache_meta(self, cache_meta):
        pass


default = DataBackend()
