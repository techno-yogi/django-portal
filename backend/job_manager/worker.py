import zmq
import time
import sys
import signal
import sqlite3
from datetime import datetime
import multiprocessing
import os

global receiver, sender, context

def signal_handler(signal, frame):
    global receiver, sender, context
    print('You pressed Ctrl+C!')
    receiver.close()
    sender.close()
    context.term()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def worker(worker_id):
    global receiver, sender, context
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.connect("tcp://localhost:5557")

    # Socket to send messages to
    sender = context.socket(zmq.PUSH)
    sender.connect("tcp://localhost:5558")

    # Connect to the SQLite database
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    # Process tasks forever
    while True:
        job_id = receiver.recv().decode('utf-8')

        # Update the job status to 'running'
        c.execute("UPDATE Jobs SET Status=?, Progress=? WHERE JobID=?", ('running', 0, job_id))
        conn.commit()

        # Simple progress indicator for the viewer
        sys.stdout.write('.')
        sys.stdout.flush()

        # Do the work
        time.sleep(1)

        # Update the job status to 'completed'
        complete_time = datetime.now().isoformat()
        c.execute("UPDATE Jobs SET Status=?, Progress=?, CompleteTime=? WHERE JobID=?", 
                  ('completed', 100, complete_time, job_id))
        conn.commit()

        # Send results to sink
        sender.send_string(job_id)

if __name__ == "__main__":
    # Create a pool of worker processes
    with multiprocessing.Pool(os.cpu_count()) as p:
        p.map(worker, range(os.cpu_count()))
