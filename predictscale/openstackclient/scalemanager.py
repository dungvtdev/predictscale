from predictmodule import config
from api.v1 import backend
from openstackclient.client import client
import threading
import time


class ScaleManager(threading.Thread):
    def __init__(self, container):
        super(ScaleManager, self).__init__()

        self._backend = backend.DBBackend.default()
        instance_id = container.instance_id
        self._group_id = self._backend.get_groupid_of_instance(instance_id)
        self._duration = config.scale_settings['minute_duration']

        self._namecount = 0

        # self.mean_accum = 0
        # self.n_point = 0

        self.high_accum_count = 0
        self.predict_accum_count = 0

    def check_scale(self, predict_list):
        high_count = 0
        for m in predict_list:
            if m >= 0.93:
                high_count = high_count + 1
        if high_count > 0:
            self.high_accum_count = self.high_accum_count + high_count
        else:
            self.high_accum_count = 0

        if self.high_accum_count >= 10:
            succ = self.scale_up()
            if succ:
                self.high_accum_count = 0
            return succ

        if predict_list:
            if predict_list[0] < 0.25:
                self.predict_accum_count = self.predict_accum_count + 1
            else:
                self.predict_accum_count = 0

            if self.predict_accum_count > 20:
                succ = self.scale_down()
                if succ:
                    self.predict_accum_count = 0
                return succ


        # if max_val < 0.3 and self.n_point > 10:
        #     tile = abs(mean_val - self.mean_accum) / (self.n_point / 2)
        #     if tile < 0.00025:
        #         return self.scale_down()
        #
        # # accum
        # if self.n_point > 0:
        #     self.mean_accum = (self.mean_accum * self.n_point + mean_val) / (self.n_point + 1)
        #     self.n_point = self.n_point + 1
        # else:
        #     self.mean_accum = mean_val
        #     self.n_point = 1

    def scale_down(self):
        if (self.is_alive()):
            return

        insts = self._backend.get_scaled_instances_by_groupid(self._group_id)
        if not insts:
            return

        rm_inst = insts[0]
        self._backend.remove_scaled_instance(rm_inst)
        client.OSClient.default().delete(rm_inst.instance_id)
        return 'down'

    def scale_up(self):
        if (self.is_alive()):
            return

        self.start()
        return 'up'

    def run(self):
        group_dict = self._backend.get_group_by_group_id(self._group_id)
        if group_dict is None:
            return

        name = 'g{group_id}.vm{count}'.format(group_id=self._group_id, count=self._namecount)
        self._namecount = self._namecount + 1
        image_id = group_dict['image']
        flavor_id = group_dict['flavor']
        net_selfservice_id = group_dict['selfservice']
        provider_name = group_dict['provider']
        user_data = self._backend.get_group_user_data_by_groupid(self._group_id)
        time_out = self._duration * 60

        time_stm = time.time()
        new_instance = client.OSClient.default().create_new_instance(name=name, image_id=image_id, \
                                                                     flavor_id=flavor_id,
                                                                     net_selfservice_id=net_selfservice_id, \
                                                                     provider_name=provider_name, user_data=user_data, \
                                                                     time_out=time_out)
        if new_instance is not None:
            self._backend.add_scaled_instance(new_instance['instance_id'], self._group_id)
            sleep_time = self._duration * 60 - (time.time() - time_stm)
            if sleep_time < 0:
                sleep_time = 0
            time.sleep(sleep_time)
