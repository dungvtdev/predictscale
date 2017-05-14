import threading
import time
from predictmodule.container import InstanceMonitorContainer
from gevent.pool import Group
from .utils import Singleton


def create_container(instance_meta):
    instance_id = instance_meta['instance_id']
    metric = instance_meta['metric']
    container = InstanceMonitorContainer(instance_meta,
                                         instance_id=instance_id,
                                         metric=metric)
    return container


def predict_container(container):
    # return container, 1
    try:
        vals, success = container.predict()
        if success:
            max_val = vals[0]
            mean_val = vals[1]
            return container, max_val, mean_val, True
        else:
            return container, None, None, False
    except Exception as e:
        print(e.message)
        return container, None, None, False


class SimpleList():

    def __init__(self):
        self.data = []
        self._lock = threading.Lock()

    def get_list(self):
        self._lock.acquire()
        try:
            return [d for d in self.data]
        finally:
            self._lock.release()

    def add_unique(self, item):
        self._lock.acquire()
        try:
            index = next((idx for idx, val in enumerate(
                self.data) if val == item), None)
            if index is not None:
                self.data[index] = item
            else:
                self.data.append(item)
        finally:
            self._lock.release()

    def remove(self, item):
        self._lock.acquire()
        try:
            self.data.remove(item)
        finally:
            self._lock.release()

    def patch(self, new_item):
        self._lock.acquire()
        try:
            for i in range(len(self.data)):
                if new_item.version_exceed(self.data[i]):
                    self.data[i] = new_item
        finally:
            self._lock.release()

    def __repr__(self):
        return self.data.__repr__()


manager = None


class PredictManager(threading.Thread):
    _default = None

    _loop_minute = 1
    # _wait_list = None
    # _pushing_list = None
    # _run_list = None

    def __init__(self, *args, **kwargs):
        super(PredictManager, self).__init__()
        self.setDaemon(True)

        self._wait_list = SimpleList()
        self._pushing_list = SimpleList()
        self._run_list = SimpleList()
        self._running = False

    @classmethod
    def default(cls):
        if cls._default is None:
            cls._default = PredictManager()
        return cls._default

    def run(self):
        print('manager running')
        count = 0
        while self._running:
            time_stm = time.time()
            print('tick %s' % count)

            self._tick_update()
            self._check_wait_list()
            self._predict()
            self._check_update_model()

            print(self._wait_list)
            print(self._pushing_list)
            print(self._run_list)

            sleep_time = self._loop_minute * 60 - (time.time() - time_stm)
            if sleep_time < 0:
                sleep_time = 0
            time.sleep(sleep_time)
            count = count + 1

    def _check_wait_list(self):
        wait_list = self._wait_list.get_list()
        for container in wait_list:
            if container.check_time_to_run():
                self._wait_list.remove(container)
                self.add_pushing(container)
        del wait_list

    def _tick_update(self):
        run_list = self._run_list.get_list()
        for container in run_list:
            container.tick_time(self._loop_minute)
        del run_list

    def _predict(self):
        run_list = self._run_list.get_list()
        group = Group()
        for container, max_val, mean_val, success in group.imap(predict_container, run_list):
            print('predict %s val %s : %s  %s' %
                  (container, max_val, mean_val, success))
        del run_list

    def _check_update_model(self):
        run_list = self._run_list.get_list()
        for container in run_list:
            if container.check_time_to_update():
                # nc = container.new_version()
                # self.add_pushing_update(nc)
                self._update_container(container)
        del run_list

    def _update_container(self, container, instance_meta=None):
        nc = container.new_version(instance_meta)
        self.add_pushing_update(nc)

    def update_container(self, instance_meta):
        instance_id = instance_meta['instance_id']
        metric = instance_meta['metric']

        inst, state = self._get_instance(instance_id, metric)
        if inst is None:
            self.add_container(instance_meta)
        elif state == 'running':
            self._update_container(inst, instance_meta)
        elif state == 'wait':
            nc = inst.new_version(instance_meta)
            self._wait_list.patch(nc)

    def add_container(self, instance_meta):
        container = create_container(instance_meta)
        container.setup_wait()
        print(container.get_data_info_string())
        if container.check_time_to_run():
            self.add_pushing(container)
        else:
            self._wait_list.add_unique(container)

    def start_thread(self):
        if not self.is_alive():
            self._running = True
            self.start()

    def stop_thread(self):
        self._running = False

    def add_pushing(self, container):
        print('add push')
        upthread = UpThread(container, self._finish_push, cache_type='temp')
        self._pushing_list.add_unique(upthread)
        upthread.push()

    def add_pushing_update(self, container):
        upthread = UpThread(container, self._patch_version,
                            cache_type='forever')
        self._pushing_list.add_unique(upthread)
        upthread.push()

    def _finish_push(self, upthread):
        self._pushing_list.remove(upthread)
        self._run_list.add_unique(upthread.get_container())

    def _patch_version(self, upthread):
        self._pushing_list.remove(upthread)
        self._run_list.patch(upthread.get_container())

    # utils func
    def _get_instance_from_list(self, instance_id, metric, flist):
        c = next((w for w in flist if w.instance_id ==
                  instance_id and w.metric == metric), None)
        return c

    def _get_instance(self, instance_id, metric):
        find = [self._wait_list, self._pushing_list, self._run_list, ]
        state = ['waiting', 'pushing', 'running']
        for idx, fl in enumerate(find):
            flist = fl.get_list()
            c = self._get_instance_from_list(instance_id, metric, flist)
            del flist
            if c is not None:
                return c, state[idx]
        return None, None

    def get_instance_status(self, instance_id, metric):
        container = self._get_instance(instance_id, metric)
        if container is not None:
            return container.get_status()
        else:
            return None


class UpThread(threading.Thread):
    def __init__(self, container, callback, cache_type='temp'):
        threading.Thread.__init__(self)
        self._container = container
        self._callback = callback
        self._cache_type = cache_type

    def push(self):
        self.start()

    def run(self):
        print('begin push')
        self._container.push(self._cache_type)
        self._callback(self)

    def get_container(self):
        return self._container
