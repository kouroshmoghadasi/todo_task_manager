from task import Task

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, title):
        task = Task(title)
        self.tasks.append(task)

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def mark_task_done(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                task.mark_done()
                break

    def get_all_tasks(self):
        return self.tasks

    def clear_all_tasks(self):
        self.tasks = []
