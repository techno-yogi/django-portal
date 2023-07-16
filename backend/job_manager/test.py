import unittest
import subprocess
import time

class TestTaskFarm(unittest.TestCase):
    def test_task_farm(self):
        # Start the sink
        sink = subprocess.Popen(['python', 'sink.py'])

        # Give the sink a second to start up
        time.sleep(1)

        # Start the workers
        workers = [subprocess.Popen(['python', 'worker.py']) for _ in range(4)]

        # Give the workers a second to start up
        time.sleep(1)

        # Start the vent
        vent = subprocess.Popen(['python', 'vent.py'], stdout=subprocess.PIPE)

        # Wait for the vent to finish
        stdout, _ = vent.communicate()

        # # Check that the vent finished correctly
        # self.assertTrue(stdout.endswith(b'Total elapsed time: %d msec\n' % 500))

        # Terminate the workers and sink
        for worker in workers:
            worker.terminate()
        sink.terminate()

if __name__ == '__main__':
    unittest.main()
