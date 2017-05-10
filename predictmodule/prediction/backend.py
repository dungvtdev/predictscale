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
    def get_instance(self, instance_id):
        pass
