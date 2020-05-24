from ravel.api.queueWorker import Job, worker, Q
from flaskthreads import AppContextThread
import unittest
import threading
import time


class TestQueue(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        threading.Thread(target=worker, daemon=True).start()

    def test_queue(self):
        try:

            queue_size = 30

            def sleep():
                time.sleep(1)
            for item in range(queue_size):
                job = Job(sleep, [])
                Q.put(job)
            self.assertEqual(queue_size, Q.qsize())
            Q.join()
            self.assertEqual(0, Q.qsize())
        except Exception as err:
            self.fail("Failed with %s" % error)
