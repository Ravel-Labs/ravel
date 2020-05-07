"""
Q creates a Queue that we can push jobs into for processing
and asynchronous handling.
"""
import threading
from flaskthreads import AppContextThread
import queue
import time
from datetime import datetime
from flask import current_app
Q = queue.Queue()


class Job():
    """
        Job class workers will be handling. 
        
        Args
            function: Initiating function for a unit of work.
            args: Arguments for the worker to use in executing this job function
            job_start: Used for logging the time of creation 
            job_end: Used for logging the time of job completion
    """
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
        Q.task_done()