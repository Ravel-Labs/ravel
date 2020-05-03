from rq import Queue, Worker, Connection
from rq.job import Job
from redis import Redis
import time
from flask import Flask, current_app

# app = Flask(__name__)
r = Redis()
print(r)
q = Queue("ravel",connection=r)
print(q)
class CustomJob(Job):
    pass


def background_task(n):
    delay = 2

    print("Task running")
    print(f"Simulating {delay} second delay")

    # TODO here we will add the processing work
    time.sleep(delay)

    # TODO

    print(len(n))
    print("Task complete")
    return len(n)


def add_task(job):
    # Here we will have to formalize the requests into job objects

    # sound object is going to take in a .wavFile, sender, email, time start, time finish
    # Emails will also be added to this queue
    print(__name__)
    print(job)
    if True:
        print('no')
        job = q.enqueue(background_task, job)
        print("wow")
        q_len = len(q)
        return f"Task {job.id} added to queue at {job.enqueued_at}, {q_len} tasks in the queue"
    return "No value for n"


'''
    Flow of the application, user submits an upload.... User does some stuff then executes a run algo route...
    Algo route is going to take in the sound file id... and fetch... create a job execute add_task
    Then we create a job that is passed into the process.... onces the processing is done it will execute 
    a send an email if the job is a sound file... we want to email the results asap
    if the task is apart of the email queue then we dont care

'''