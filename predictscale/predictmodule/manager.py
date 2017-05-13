import threading
import time
from predictmodule.container import InstanceMonitorContainer
from gevent.pool import Group


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

    def replace(self, new_item):
        self._lock.acquire()
        try:
            for i in range(len(self.data)):
                if new_item.equal(self.data[i]):
                    self.data[i] = new_item
        finally:
            self._lock.release()

    def __repr__(self):
        return self.data.__repr__()


class PredictManager(threading.Thread):
    _loop_minute = 1
    _wait_list = None
    _pushing_list = None
    _run_list = None

    _running = False

    def __init__(self):
        super(PredictManager, self).__init__()
        self.setDaemon(True)

        self._wait_list = SimpleList()
        self._pushing_list = SimpleList()
        self._run_list = SimpleList()

    def run(self):
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
                nc = container.new_version()
                self.add_pushing_update(nc)
        del run_list

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
        self._run_list.replace(upthread.get_container())


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
