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
            # Ensure category is set if provided separately
            if category and getattr(task, "category", None) is None:
                task.category = category
        else:
            task = Task(title_or_task, category=category)
        # Ensure title is a plain string (compatibility)
        if hasattr(task, "title") and not isinstance(task.title, str):
            try:
                task.title = str(task.title)
            except Exception:
                pass
        self.tasks.append(task)
        return task

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if getattr(task, "id", None) != task_id]

    def mark_task_done(self, task_id):
        for task in self.tasks:
            if getattr(task, "id", None) == task_id:
                if hasattr(task, "mark_done"):
                    task.mark_done()
                else:
                    # fallback: set a done flag if exists
                    setattr(task, "done", True)
                break

    def get_all_tasks(self):
        return self.tasks

    def clear_all_tasks(self):
        self.tasks = []

    def get_tasks(self):
        """
        Compatibility helper for tests: return the list of tasks.
        """
        return self.tasks
