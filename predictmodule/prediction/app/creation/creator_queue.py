import Queue
import threading
from . import container


class CreatorQueue(object):
    queue = None
    out_queue = None
    creators = None

    def __init__(self, creator_cls=None, n_creator=4):
        self._n_creator = n_creator
        self._creator_cls = creator_cls

    def start(self):
        if self.creators is not None:
            raise Exception('CreatorQueue start can\'t call multiple time')

        self.queue = Queue.Queue()
        self.creators = []
        for i in range(self._n_creator):
            c = self._creator_cls(self.queue, out_queue)
            c.daemon = True
            self.creators.append(c)
            c.start()

    def put(self, container):
        self.queue.put(container)
        container.status = container.PENDING

    def pop_finishs(self):
        rl = []
        while not self.queue.empty():
            c = self.queue.get()
            rl.append(c)
        return rl


class Creator(theading.Thread):
    def __init__(self, queue, out_queue):
        self.queue = queue
        self.out_queue = out_queue

    def run(self):
        while True:
            container = self.queue.get()
            self._container = container
            container.create()
            self.out_queue.put(container)
