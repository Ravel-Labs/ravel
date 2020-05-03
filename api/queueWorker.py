"""
Q creates a Queue that we can push jobs into for processing
and asynchronous handling.
"""
import threading
import queue

Q = queue.Queue()

# TODO I need to create a job tasks for the processing layer
# Each job coming from some endpoint () will be added to the queue

def worker():
    """
    Worker defines what needs to be done during the task
    """
    while True:
        item = Q.get()
        print(f'Working on {item}')
        print(f'Finished {item}')
        Q.task_done()


# turn-on the worker thread
threading.Thread(target=worker, daemon=True).start()

# send thirty task requests to the worker
for item in range(30):
    Q.put(item)
print('All task requests sent\n', end='')

# block until all tasks are done
Q.join()
print('All work completed')
