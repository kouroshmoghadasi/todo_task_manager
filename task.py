from datetime import datetime
import uuid

class Task:
    def __init__(self, title, category="Personal", completed=False, created_at=None, done_at=None, task_id=None, due_date=None):
        self.id = task_id or str(uuid.uuid4())
        self.title = title
        self.category = category
        self.completed = completed
        self.created_at = created_at or datetime.now().isoformat()
        self.done_at = done_at
        # due_date: YYYY-MM-DD or None
        self.due_date = due_date

    def mark_done(self):
        self.completed = True
        self.done_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "completed": self.completed,
            "created_at": self.created_at,
            "done_at": self.done_at,
            "due_date": self.due_date
        }

    @staticmethod
    def from_dict(data):
        return Task(
            title=data["title"],
            category=data.get("category", "Personal"),
            completed=data.get("completed", False),
            created_at=data.get("created_at"),
            done_at=data.get("done_at"),
            task_id=data.get("id"),
            due_date=data.get("due_date")
        )
