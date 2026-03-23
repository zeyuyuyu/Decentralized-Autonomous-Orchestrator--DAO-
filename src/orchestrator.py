import time
import threading
import logging

class TaskScheduler:
    def __init__(self, max_concurrent_tasks=5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue = []
        self.active_tasks = []
        self.lock = threading.Lock()

    def schedule_task(self, task):
        with self.lock:
            self.task_queue.append(task)
            self.process_queue()

    def process_queue(self):
        while len(self.active_tasks) < self.max_concurrent_tasks and self.task_queue:
            task = self.task_queue.pop(0)
            self.active_tasks.append(task)
            threading.Thread(target=self.execute_task, args=(task,)).start()

    def execute_task(self, task):
        try:
            task.execute()
        except Exception as e:
            logging.error(f"Error executing task: {e}")
        finally:
            with self.lock:
                self.active_tasks.remove(task)
                self.process_queue()

class Task:
    def __init__(self, name, function, *args, **kwargs):
        self.name = name
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        self.function(*self.args, **self.kwargs)

class Orchestrator:
    def __init__(self):
        self.task_scheduler = TaskScheduler()

    def run_task(self, name, function, *args, **kwargs):
        task = Task(name, function, *args, **kwargs)
        self.task_scheduler.schedule_task(task)
