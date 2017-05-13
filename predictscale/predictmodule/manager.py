import threading
import time
from predictmodule.container import InstanceMonitorContainer
import gevent


def create_container(instance_meta):
    instance_id = instance_meta['instance_id']
    metric = instance_meta['metric']
    container = InstanceMonitorContainer(instance_meta,
                                         instance_id=instance_id,
                                         metric=metric)
    return container


def predict_container(container):
    return container, container.predict()


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

            self._check_wait_list()
            self._predict()
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
            if container.check_time_to_run(self._loop_minute):
                self._wait_list.remove(container)
                self.add_pushing(container)

    def _predict(self):
        threads = []
        run_list = self._run_list.get_list()
        for container in run_list:
            t = gevent.spawn(predict_container, container)
            threads.append(t)

        gevent.joinall(threads)
        for t in threads:
            container, val = t.value
            if not t.successful():
                print('%s get fail' % container)
            else:
                print('%s val %s' % (container, val))

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
        upthread = UpThread(container, self._finish_push)
        self._pushing_list.add_unique(upthread)
        upthread.push()

    def _finish_push(self, upthread):
        self._pushing_list.remove(upthread)
        self._run_list.add_unique(upthread.get_container())


class UpThread(threading.Thread):
    def __init__(self, container, callback):
        threading.Thread.__init__(self)
        self._container = container
        self._callback = callback

    def push(self):
        self.start()

    def run(self):
        print('begin push')
        self._container.push()
        self._callback(self)

    def get_container(self):
        return self._container
