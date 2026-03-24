import os
import time
import random
import multiprocessing as mp

class AutonomousOrchestrator:
    def __init__(self, num_workers=4, max_load=80):
        self.num_workers = num_workers
        self.max_load = max_load
        self.worker_processes = []
        self.start_workers()

    def start_workers(self):
        for _ in range(self.num_workers):
            process = mp.Process(target=self.worker_loop)
            process.start()
            self.worker_processes.append(process)

    def worker_loop(self):
        while True:
            # Simulate some work
            work_duration = random.uniform(1, 5)
            time.sleep(work_duration)

            # Check the system load
            load = os.getloadavg()[0]
            if load > self.max_load:
                # Scale up by starting a new worker
                new_process = mp.Process(target=self.worker_loop)
                new_process.start()
                self.worker_processes.append(new_process)
                print(f'Scaled up, now have {len(self.worker_processes)} workers')
            elif len(self.worker_processes) > self.num_workers:
                # Scale down by terminating a worker
                worker_to_terminate = self.worker_processes.pop()
                worker_to_terminate.terminate()
                print(f'Scaled down, now have {len(self.worker_processes)} workers')

if __name__ == '__main__':
    orchestrator = AutonomousOrchestrator()
    orchestrator.start_workers()
