"""
Q creates a Queue that we can push jobs into for processing
and asynchronous handling.
"""

from flaskthreads import AppContextThread
from datetime import datetime
import queue
Q = queue.Queue()


class Job():
    """
        Job class workers will be handling.

        Args
            function: Initiating function for a unit of work.
            args: Arguments for the worker to use
            in executing this job function
            job_start: Used for logging the time of creation
            job_end: Used for logging the time of job completion
    """
    def __repr__(self):
        return f"Job started at {self.job_start} : ended {self.job_end}"

    def __init__(self, function, args):
        self.function = function
        self.args = args
        self.job_start = datetime.now()
        self.job_end = None

    def execute(self):
        self.function(*self.args)


def worker():
    """
    Worker defines what needs to be done during the task
    """
    while True:
        item = Q.get()
        print(f'Working on {item}')
        item.execute()
        print(f'Finished {item}, {Q.qsize()} left')
        setattr(item, 'job_end', datetime.now())
        Q.task_done()
