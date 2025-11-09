import unittest
import sys
import os

# Add project root to sys.path so imports work when running tests
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from task_manager import TaskManager
from task import Task
from category_manager import CategoryManager

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.task_manager = TaskManager()
        self.category_manager = CategoryManager()
    
    def tearDown(self):
        # Clean up possible JSON files created by the app to avoid side effects between tests
        for fname in ("tasks.json", "categories.json"):
            path = os.path.join(project_root, fname)
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

    def test_add_task(self):
        task = Task("تست", "توضیحات تست", "عادی")
        self.task_manager.add_task(task)
        tasks = self.task_manager.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "تست")

    def test_delete_task(self):
        task = Task("تست", "توضیحات تست", "عادی")
        self.task_manager.add_task(task)
        self.task_manager.delete_task(task.id)
        tasks = self.task_manager.get_tasks()
        self.assertEqual(len(tasks), 0)

    def test_category_management(self):
        self.category_manager.add_category("کار")
        categories = self.category_manager.get_categories()
        self.assertIn("کار", categories)

if __name__ == "__main__":
    unittest.main()