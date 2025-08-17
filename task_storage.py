import json
import os
from task import Task

class TaskStorage:
    def __init__(self, filename="tasks.json"):
        self.filename = filename

    def save_tasks(self, tasks):
        data = [task.to_dict() for task in tasks]
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_tasks(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [Task.from_dict(item) for item in data]
