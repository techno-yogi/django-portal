import zmq
import time
import signal
import sqlite3
import sys
from datetime import datetime

global context, receiver, conn

def signal_handler(signal, frame):
    global receiver, context, conn
    print('You pressed Ctrl+C!')
    receiver.close()
    context.term()
    conn.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def sink():
    global receiver, context, conn
    # Prepare our context and sockets
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:5558")

    # Connect to the SQLite database
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    # Wait for start of batch
    s = receiver.recv()

    # Start our clock now
    tstart = time.time()

    # Process 100 confirmations
    while True:
        job_id = receiver.recv().decode('utf-8')

        # Exit if we receive the "EXIT" signal
        if job_id == "EXIT":
            break

        # Update the job status to 'completed' in the database
        complete_time = datetime.now().isoformat()
        c.execute("UPDATE Jobs SET Status=?, Progress=?, CompleteTime=? WHERE JobID=?", 
                  ('completed', 100, complete_time, job_id))
        conn.commit()

        # if task_nbr % 10 == 0:
        #     sys.stdout.write(':')
        # else:
        #     sys.stdout.write('.')
        # sys.stdout.flush()

    # Calculate and report duration of batch
    tend = time.time()
    print("Total elapsed time: %d msec" % ((tend - tstart) * 1000))

if __name__ == "__main__":
    sink()
