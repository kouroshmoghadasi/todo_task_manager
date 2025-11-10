from task import Task


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, title_or_task, category="Personal"):
        """
        Accept either a Task instance or a title string.
        If a Task instance is provided, append it directly.
        If a title string is provided, create a new Task.
        """
        if isinstance(title_or_task, Task):
            task = title_or_task
            if category and getattr(task, "category", None) is None:
                task.category = category
        else:
            task = Task(title_or_task, category=category)

        if hasattr(task, "title") and not isinstance(task.title, str):
            try:
                task.title = str(task.title)
            except Exception:
                pass

        self.tasks.append(task)
        return task

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if getattr(t, "id", None) != task_id]

    def mark_task_done(self, task_id):
        for t in self.tasks:
            if getattr(t, "id", None) == task_id:
                if hasattr(t, "mark_done"):
                    t.mark_done()
                else:
                    setattr(t, "done", True)
                break

    def get_all_tasks(self):
        return list(self.tasks)

    def clear_all_tasks(self):
        self.tasks = []

    # Compatibility helper used by tests
    def get_tasks(self):
        return list(self.tasks)
