'''
instance:{
    instance_id,
    period : so phut,
    n_period_to_train: so lan period bat dau train,
    train_params,
    n_predict: so diem (phut) dc predic,
    auto_retrain_period: so phut train lai network
}
'''


class DataBackend(object):
    def get_instance(self, instance_id):
        pass
