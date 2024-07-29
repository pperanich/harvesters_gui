from qtpy.QtCore import QMutexLocker, QThread
from harvesters.core import ThreadBase


class _PyQtThread(ThreadBase):
    def __init__(self, parent=None, mutex=None, worker=None, update_cycle_us=1):
        super().__init__(mutex=mutex)

        self._thread = _ThreadImpl(
            base=self, parent=parent, worker=worker, update_cycle_us=update_cycle_us
        )

    def acquire(self):
        return self._thread.acquire()

    def release(self):
        self._thread.release()

    @property
    def worker(self):
        return self._thread.worker

    @worker.setter
    def worker(self, obj):
        self._thread.worker = obj

    @property
    def mutex(self):
        return self._mutex

    @property
    def id_(self):
        return self._thread.id_

    def is_running(self) -> bool:
        return self._is_running

    def join(self):
        pass

    def _internal_stop(self):
        self._thread.stop()
        self._thread.wait()
        self._is_running = False

    def _internal_start(self) -> None:
        self._is_running = True
        self._thread.start()


class _ThreadImpl(QThread):
    def __init__(
        self,
        base: ThreadBase,
        parent=None,
        worker=None,
        update_cycle_us=1,
    ):
        super().__init__(parent)

        self._worker = worker
        self._base = base
        self._update_cycle_us = update_cycle_us

    def stop(self):
        with QMutexLocker(self._base._mutex):
            self._base._is_running = False

    def run(self):
        while self._base.is_running():
            if self._worker:
                self._worker()
                # Force the current thread to sleep for some microseconds:
                self.usleep(self._update_cycle_us)

    def acquire(self):
        return QMutexLocker(self._base._mutex)

    def release(self):
        pass

    @property
    def worker(self):
        return self._worker

    @worker.setter
    def worker(self, obj):
        self._worker = obj

    @property
    def id_(self):
        thread_id = self.currentThreadId()
        if thread_id is None:
            thread_id = -1
        return int(thread_id)
