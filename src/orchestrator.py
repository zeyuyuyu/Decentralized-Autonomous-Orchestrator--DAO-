import asyncio
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import heapq

class TaskPriority(Enum):
    HIGH = 0
    MEDIUM = 1
    LOW = 2

@dataclass(order=True)
class Task:
    priority: TaskPriority
    timestamp: datetime
    name: str
    callback: Callable
    args: tuple = ()
    kwargs: Dict[str, Any] = None

    def __post_init__(self):
        self.kwargs = self.kwargs or {}

class Orchestrator:
    def __init__(self):
        self._task_queue: List[Task] = []
        self._running = False
        self._results: Dict[str, Any] = {}

    async def submit_task(self, name: str, callback: Callable,
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         *args, **kwargs) -> None:
        task = Task(
            priority=priority,
            timestamp=datetime.now(),
            name=name,
            callback=callback,
            args=args,
            kwargs=kwargs
        )
        heapq.heappush(self._task_queue, task)

    async def execute_task(self, task: Task) -> Any:
        try:
            if asyncio.iscoroutinefunction(task.callback):
                result = await task.callback(*task.args, **task.kwargs)
            else:
                result = task.callback(*task.args, **task.kwargs)
            self._results[task.name] = result
            return result
        except Exception as e:
            self._results[task.name] = e
            raise

    async def run(self):
        self._running = True
        while self._running and self._task_queue:
            task = heapq.heappop(self._task_queue)
            await self.execute_task(task)

    def stop(self):
        self._running = False

    def get_result(self, task_name: str) -> Optional[Any]:
        return self._results.get(task_name)

    @property
    def pending_tasks(self) -> int:
        return len(self._task_queue)

    @property
    def results(self) -> Dict[str, Any]:
        return self._results.copy()

    async def clear(self):
        self._task_queue.clear()
        self._results.clear()
