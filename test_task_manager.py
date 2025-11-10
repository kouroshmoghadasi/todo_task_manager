import unittest
import sys
import os

# Ensure project root is on sys.path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from task_manager import TaskManager
from task import Task
from category_manager import CategoryManager


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.task_manager = TaskManager()
        self.category_manager = CategoryManager()
        # ensure clean state
        self.task_manager.clear_all_tasks()
        self.category_manager.clear_categories()

    def tearDown(self):
        # Remove any persisted files created during tests
        for fname in ("tasks.json", "categories.json"):
            path = os.path.join(project_root, fname)
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

    def test_add_task(self):
        task = Task("Test", "Test description", "General")
        self.task_manager.add_task(task)
        tasks = self.task_manager.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, "Test")

    def test_delete_task(self):
        task = Task("Test", "Test description", "General")
        added = self.task_manager.add_task(task)
        self.task_manager.delete_task(added.id)
        tasks = self.task_manager.get_tasks()
        self.assertEqual(len(tasks), 0)

    def test_category_management(self):
        added = self.category_manager.add_category("Work")
        categories = self.category_manager.get_categories()
        self.assertTrue(added)
        self.assertIn("Work", categories)


if __name__ == "__main__":
    unittest.main()