import zmq
import time
import signal
import sqlite3
import random
from datetime import datetime
import sys

global sink, sender, context, conn

def signal_handler(signal, frame):
    global sink, sender, context, conn
    print('You pressed Ctrl+C!')
    sender.close()
    sink.close()
    context.term()
    conn.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def vent():
    global sink, sender, context, conn
    # Prepare our context and sockets
    context = zmq.Context()

    # Socket to send messages on
    sender = context.socket(zmq.PUSH)
    sender.bind("tcp://*:5557")

    # Socket with direct access to the sink: used to synchronize start of batch
    sink = context.socket(zmq.PUSH)
    sink.connect("tcp://localhost:5558")

    # Connect to the SQLite database
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()

    print("Press Enter when the workers are ready: ")
    _ = input()
    print("Sending tasks to workers...")

    # The first message is "0" and signals start of batch
    sink.send(b'0')

    # Initialize random number generator
    random.seed()

    # Send 100 jobs
    total_msec = 0
    for task_nbr in range(100):
        # Random workload from 1 to 100 msecs
        workload = random.randint(1, 100)
        total_msec += workload
        sender.send_string(u'%i' % task_nbr)

        # Create a new job in the database
        submit_time = datetime.now().isoformat()
        c.execute("INSERT INTO Jobs VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                  (str(task_nbr), 'queued', 0, submit_time, workload, None, '/output/dir', 'config'))
        conn.commit()

        sender.send_string(u'%i' % task_nbr)

    print("Total expected cost: %s msec" % total_msec)
    sender.send_string('EXIT')
    
    time.sleep(1)  # Give 0MQ time to deliver

if __name__ == "__main__":
    vent()
