import zmq
import json
import uuid
from typing import Dict, List, Any
from datetime import datetime

class TaskOrchestrator:
    def __init__(self, host: str = '*', port: int = 5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(f'tcp://{host}:{port}')
        self.tasks: Dict[str, Dict] = {}
        self.workers: Dict[str, datetime] = {}

    def register_worker(self, worker_id: str) -> None:
        self.workers[worker_id] = datetime.now()

    def submit_task(self, task_spec: Dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            'spec': task_spec,
            'status': 'pending',
            'created_at': datetime.now(),
            'worker_id': None
        }
        return task_id

    def assign_task(self, worker_id: str) -> Dict[str, Any]:
        available_tasks = [
            (tid, task) for tid, task in self.tasks.items()
            if task['status'] == 'pending'
        ]
        if not available_tasks:
            return None

        task_id, task = available_tasks[0]
        task['status'] = 'running'
        task['worker_id'] = worker_id
        return {'task_id': task_id, 'spec': task['spec']}

    def update_task_status(self, task_id: str, status: str, result: Any = None) -> None:
        if task_id in self.tasks:
            self.tasks[task_id].update({
                'status': status,
                'result': result,
                'completed_at': datetime.now()
            })

    def run(self) -> None:
        print('Task Orchestrator started...')
        while True:
            worker_id, *msg_parts = self.socket.recv_multipart()
            message = json.loads(msg_parts[-1].decode())
            
            if message['type'] == 'register':
                self.register_worker(worker_id.decode())
                response = {'status': 'registered'}
            
            elif message['type'] == 'request_task':
                task = self.assign_task(worker_id.decode())
                response = {'status': 'task_assigned', 'task': task}
            
            elif message['type'] == 'task_complete':
                self.update_task_status(
                    message['task_id'],
                    'completed',
                    message.get('result')
                )
                response = {'status': 'acknowledged'}
            
            self.socket.send_multipart([
                worker_id,
                json.dumps(response).encode()
            ])

if __name__ == '__main__':
    orchestrator = TaskOrchestrator()
    orchestrator.run()