import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from tkcalendar import DateEntry
import csv
import winsound

from task_manager import TaskManager
from task_storage import TaskStorage
from category_manager import CategoryManager
from dialogs import AddCategoryDialog, DeleteCategoryDialog, RenameCategoryDialog, EditTaskDialog


class TaskManagerApp:
    def __init__(self) -> None:
        # Core services
        self.storage = TaskStorage()
        self.manager = TaskManager()
        self.manager.tasks = self.storage.load_tasks()
        self.category_manager = CategoryManager()
        self.category_manager.load()

        # State
        self.LOG_FILE = "activity.log"
        self.current_tasks = []

        # Tk root
        self.window = tk.Tk()
        self.window.title("To-Do Task Manager")
        self.window.resizable(True, True)
        self.window.configure(bg="#f0f0f0")
        self.window.bind("<Escape>", lambda e: self.window.destroy())

        # Center window
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        win_width = 1100
        win_height = 600
        x = int((screen_width - win_width) / 2)
        y = int((screen_height - win_height) / 2)
        self.window.geometry(f"{win_width}x{win_height}+{x}+{y}")

        # Layout: two columns
        self.main_frame = tk.Frame(self.window, bg="#f0f0f0")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Left: actions
        self.button_frame = tk.LabelFrame(self.main_frame, text="Actions", bg="#e0e0e0",
                                          font=("Segoe UI", 11, "bold"), relief="ridge", borderwidth=4)
        self.button_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=5)

        tk.Button(self.button_frame, text="Add Task", width=20, command=self.add_task,
                  bg="#4CAF50", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)
        tk.Button(self.button_frame, text="Delete Task", width=20, command=self.delete_task,
                  bg="#f44336", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)
        tk.Button(self.button_frame, text="Mark as Done", width=20, command=self.mark_done,
                  bg="#2196F3", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)
        tk.Button(self.button_frame, text="Edit Task", width=20, command=self.edit_task,
                  bg="#9C27B0", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)
        tk.Button(self.button_frame, text="Show All Tasks", width=20, command=self.show_all_tasks,
                  bg="#218071", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)
        tk.Button(self.button_frame, text="Today's Tasks", width=20, command=self.today_tasks,
                  bg="#622180", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)
        tk.Button(self.button_frame, text="Export to CSV", width=20, command=self.export_to_csv,
                  bg="#ff9800", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

        # Stats button
        tk.Button(self.button_frame, text="Task Stats", width=20, command=self.show_stats,
                  bg="#607D8B", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

        # Category group
        manage_cat_frame = tk.LabelFrame(self.button_frame, text="Categories", bg="#e0e0e0",
                                         font=("Segoe UI", 10, "bold"), relief="groove", borderwidth=3)
        manage_cat_frame.pack(pady=(4, 8), padx=8, fill="x")
        tk.Button(manage_cat_frame, text="+ Add Category", width=20, command=self.add_new_category,
                  bg="#666", fg="white", font=("Segoe UI", 10)).pack(pady=(6, 2))
        tk.Button(manage_cat_frame, text="Rename Category", width=20, command=self.edit_category_dialog,
                  bg="#3F51B5", fg="white", font=("Segoe UI", 10)).pack(pady=(0, 2))
        tk.Button(manage_cat_frame, text="Delete Category", width=20, command=self.delete_category_dialog,
                  bg="#8B0000", fg="white", font=("Segoe UI", 10)).pack(pady=(0, 6))

        # Right: inputs and list
        self.right_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        self.right_frame.columnconfigure(0, weight=1)

        # Inputs row
        input_frame = tk.Frame(self.right_frame, bg="#f0f0f0")
        input_frame.pack(fill="x", pady=(0, 5))
        self.entry = tk.Entry(input_frame, width=30, font=("Segoe UI", 12))
        self.entry.pack(side="left", padx=(0, 6))
        self.category_combo = ttk.Combobox(input_frame, values=self.category_manager.get_task_categories(),
                                           state="readonly", font=("Segoe UI", 11), width=14)
        default_category = "Personal" if "Personal" in self.category_manager.get_task_categories() else (
            self.category_manager.get_task_categories()[0] if self.category_manager.get_task_categories() else "")
        self.category_combo.set(default_category)
        self.category_combo.pack(side="left", padx=(0, 6))
        self.date_picker = DateEntry(input_frame, width=14, font=("Segoe UI", 11), date_pattern='yyyy-mm-dd')
        self.date_picker.pack(side="left", padx=(0, 6))
        tk.Label(input_frame, text="Due:", bg="#f0f0f0", font=("Segoe UI", 10)).pack(side="left", padx=(4,0))
        self.due_picker = DateEntry(input_frame, width=12, font=("Segoe UI", 11), date_pattern='yyyy-mm-dd')
        self.due_picker.pack(side="left", padx=(0, 6))

        # Filters row
        filter_frame = tk.Frame(self.right_frame, bg="#f0f0f0")
        filter_frame.pack(fill="x", pady=(0, 8))
        self.category_filter_combo = ttk.Combobox(filter_frame, values=self.category_manager.get_all_categories(),
                                                  state="readonly", font=("Segoe UI", 11), width=12)
        self.category_filter_combo.set("All")
        self.category_filter_combo.pack(side="left", padx=(0, 6))
        self.search_entry = tk.Entry(filter_frame, width=28, font=("Segoe UI", 12))
        self.search_entry.pack(side="left", padx=(0, 6))
        self.search_entry.bind("<Return>", self.search_tasks)
        tk.Button(filter_frame, text="Search", command=self.search_tasks,
                  bg="#009688", fg="white", font=("Segoe UI", 11)).pack(side="left", padx=(0, 4))
        tk.Button(filter_frame, text="Filter", command=self.filter_by_date,
                  bg="#555", fg="white", font=("Segoe UI", 11)).pack(side="left")

        # List + scrollbar
        list_frame = tk.Frame(self.right_frame, bg="#f0f0f0")
        list_frame.pack(fill="both", expand=True)
        self.task_listbox = tk.Listbox(list_frame, width=60, height=20, font=("Segoe UI", 12))
        self.task_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.task_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.task_listbox.configure(yscrollcommand=scrollbar.set)
        self.task_listbox.bind("<Double-Button-1>", self.edit_task)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.right_frame, textvariable=self.status_var, anchor="w",
                              bg="#e9e9e9", fg="#333", font=("Segoe UI", 10))
        status_bar.pack(fill="x", pady=(6, 0))

        # Initial load
        self.rebuild_category_options()
        self.refresh_listbox("today")
        # periodic reminder check
        self._notified_ids = set()
        self.window.after(30000, self._check_due_tasks)

    def _check_due_tasks(self) -> None:
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            for t in self.manager.get_all_tasks():
                if getattr(t, 'completed', False):
                    continue
                due = getattr(t, 'due_date', None)
                if due and due <= today and t.id not in self._notified_ids:
                    try:
                        winsound.Beep(1200, 250)
                        winsound.Beep(900, 250)
                    except Exception:
                        pass
                    messagebox.showinfo("Task Reminder", f"'{t.title}' is due ({due}).")
                    self._notified_ids.add(t.id)
        finally:
            self.window.after(30000, self._check_due_tasks)

    # ---------- Helpers ----------
    def log_action(self, action: str, task_title: str = "") -> None:
        try:
            with open(self.LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action} {task_title}\n")
        except Exception:
            pass

    @staticmethod
    def play_beep() -> None:
        try:
            winsound.Beep(1000, 200)
        except Exception:
            pass

    def center_over_main(self, dlg: tk.Toplevel) -> None:
        try:
            dlg.update_idletasks()
            px = self.window.winfo_rootx()
            py = self.window.winfo_rooty()
            pw = self.window.winfo_width()
            ph = self.window.winfo_height()
            dw = dlg.winfo_width()
            dh = dlg.winfo_height()
            x = px + max(0, (pw - dw) // 2)
            y = py + max(0, (ph - dh) // 2)
            dlg.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def rebuild_category_options(self) -> None:
        # Sync combos with current categories
        task_cats = self.category_manager.get_task_categories()
        all_cats = self.category_manager.get_all_categories()
        try:
            self.category_combo['values'] = task_cats
            if self.category_combo.get() not in task_cats:
                fallback = "Personal" if "Personal" in task_cats else (task_cats[0] if task_cats else "")
                self.category_combo.set(fallback)
        except Exception:
            pass
        try:
            self.category_filter_combo['values'] = all_cats
            if self.category_filter_combo.get() not in all_cats:
                self.category_filter_combo.set("All")
        except Exception:
            pass

    # ---------- Actions ----------
    def refresh_listbox(self, date_filter=None, category_filter=None, search_term="") -> None:
        self.task_listbox.delete(0, tk.END)
        tasks = list(self.manager.get_all_tasks())

        if date_filter == "today":
            today = datetime.now().strftime("%Y-%m-%d")
            tasks = [t for t in tasks if t.created_at.split("T")[0] == today]
        elif isinstance(date_filter, str):
            tasks = [t for t in tasks if t.created_at.split("T")[0] == date_filter]

        if category_filter and category_filter != "All":
            tasks = [t for t in tasks if t.category == category_filter]

        if search_term.strip():
            tasks = [t for t in tasks if search_term.lower() in t.title.lower()]

        self.current_tasks = tasks
        for task in tasks:
            overdue = False
            try:
                if getattr(task, 'due_date', None) and not task.completed:
                    overdue = datetime.now().strftime("%Y-%m-%d") > task.due_date
            except Exception:
                overdue = False
            prefix = "⏰ " if overdue else ""
            display = f"{prefix}✔️ {task.title} ({task.category})" if task.completed else f"{prefix}{task.title} ({task.category})"
            self.task_listbox.insert(tk.END, display)

        try:
            all_tasks = self.manager.get_all_tasks()
            total_count = len(all_tasks)
            completed_count = sum(1 for t in all_tasks if getattr(t, 'completed', False))
            pending_count = total_count - completed_count
            self.status_var.set(
                f"Showing {len(tasks)} of {total_count} | Completed {completed_count} | Pending {pending_count}"
            )
        except Exception:
            pass

    def add_task(self) -> None:
        title = self.entry.get().strip()
        category = self.category_combo.get()
        if not title:
            messagebox.showwarning("Empty Task", "Please enter a task.")
            return
        task = self.manager.add_task(title, category)
        try:
            task.due_date = self.due_picker.get_date().strftime("%Y-%m-%d")
        except Exception:
            task.due_date = None
        self.storage.save_tasks(self.manager.get_all_tasks())
        self.entry.delete(0, tk.END)
        self.refresh_listbox("today")
        self.log_action("Task Added:", title)
        self.play_beep()

    def delete_task(self) -> None:
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a task to delete.")
            return
        index = selected[0]
        task = self.current_tasks[index]
        self.manager.delete_task(task.id)
        self.storage.save_tasks(self.manager.get_all_tasks())
        self.refresh_listbox("today")
        self.log_action("Task Deleted:", task.title)

    def mark_done(self) -> None:
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a task to mark as done.")
            return
        index = selected[0]
        task = self.current_tasks[index]
        self.manager.mark_task_done(task.id)
        self.storage.save_tasks(self.manager.get_all_tasks())
        self.refresh_listbox("today")
        self.log_action("Task Completed:", task.title)
        self.play_beep()

    def edit_task(self, event=None) -> None:
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a task to edit.")
            return
        index = selected[0]
        task = self.current_tasks[index]

        def on_saved(_task):
            self.storage.save_tasks(self.manager.get_all_tasks())
            self.refresh_listbox("today", self.category_filter_combo.get(), self.search_entry.get().strip())
            self.log_action("Task Edited:", _task.title)
            self.play_beep()

        EditTaskDialog(self.window, task, self.category_manager, on_saved)

    def today_tasks(self) -> None:
        self.refresh_listbox("today")
        self.log_action("Filter:", "Today")

    def filter_by_date(self) -> None:
        selected_date = self.date_picker.get_date().strftime("%Y-%m-%d")
        self.refresh_listbox(selected_date, self.category_filter_combo.get(), self.search_entry.get().strip())
        self.log_action("Filter by Date:", selected_date)

    def show_all_tasks(self) -> None:
        self.refresh_listbox(None, self.category_filter_combo.get(), self.search_entry.get().strip())
        self.log_action("Filter:", "All Tasks")

    def search_tasks(self, event=None) -> None:
        term = self.search_entry.get().strip()
        self.refresh_listbox(date_filter="today", category_filter=self.category_filter_combo.get(), search_term=term)
        self.log_action("Search:", term)

    def export_to_csv(self) -> None:
        filename = f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Category", "Completed", "Created At", "Done At"])
            for task in self.manager.get_all_tasks():
                writer.writerow([task.id, task.title, task.category, task.completed, task.created_at, task.done_at])
        messagebox.showinfo("Exported", f"Tasks exported to {filename}")
        self.log_action("Tasks Exported:", filename)

    def show_stats(self) -> None:
        all_tasks = list(self.manager.get_all_tasks())
        total_count = len(all_tasks)
        completed_count = sum(1 for t in all_tasks if getattr(t, 'completed', False))
        pending_count = total_count - completed_count

        # همچنین آمار نمایشی (فیلتر فعلی)
        visible_count = len(self.current_tasks)
        visible_completed = sum(1 for t in self.current_tasks if getattr(t, 'completed', False))
        visible_pending = visible_count - visible_completed

        dlg = tk.Toplevel(self.window)
        dlg.title("Task Statistics")
        dlg.resizable(False, False)
        dlg.transient(self.window)
        dlg.grab_set()

        frame = tk.Frame(dlg, bg="#f7f7f7", padx=16, pady=14)
        frame.pack(fill="both", expand=True)

        header = tk.Label(frame, text="Overall", bg="#f7f7f7", font=("Segoe UI", 11, "bold"))
        header.grid(row=0, column=0, sticky="w")
        tk.Label(frame, text=f"Total: {total_count}", bg="#f7f7f7", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w")
        tk.Label(frame, text=f"Completed: {completed_count}", bg="#f7f7f7", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w")
        tk.Label(frame, text=f"Pending: {pending_count}", bg="#f7f7f7", font=("Segoe UI", 10)).grid(row=3, column=0, sticky="w")

        sep = tk.Label(frame, text="", bg="#f7f7f7")
        sep.grid(row=4, column=0, pady=(6, 6))

        header2 = tk.Label(frame, text="Current View", bg="#f7f7f7", font=("Segoe UI", 11, "bold"))
        header2.grid(row=5, column=0, sticky="w")
        tk.Label(frame, text=f"Shown: {visible_count}", bg="#f7f7f7", font=("Segoe UI", 10)).grid(row=6, column=0, sticky="w")
        tk.Label(frame, text=f"Completed: {visible_completed}", bg="#f7f7f7", font=("Segoe UI", 10)).grid(row=7, column=0, sticky="w")
        tk.Label(frame, text=f"Pending: {visible_pending}", bg="#f7f7f7", font=("Segoe UI", 10)).grid(row=8, column=0, sticky="w")

        tk.Button(frame, text="Close", command=dlg.destroy, bg="#ddd", fg="#333", width=10).grid(row=9, column=0, sticky="e", pady=(10,0))

        # Center over main
        try:
            dlg.update_idletasks()
            px = self.window.winfo_rootx()
            py = self.window.winfo_rooty()
            pw = self.window.winfo_width()
            ph = self.window.winfo_height()
            dw = dlg.winfo_width()
            dh = dlg.winfo_height()
            x = px + max(0, (pw - dw) // 2)
            y = py + max(0, (ph - dh) // 2)
            dlg.geometry(f"+{x}+{y}")
        except Exception:
            pass

    # ---------- Category dialogs ----------
    def add_new_category(self) -> None:
        def on_added(name: str):
            self.rebuild_category_options()
            try:
                self.category_combo.set(name)
            except Exception:
                pass

        AddCategoryDialog(self.window, self.category_manager, on_added)

    def delete_category_dialog(self) -> None:
        if not self.category_manager.get_task_categories():
            messagebox.showinfo("No Categories", "There are no user categories to delete.")
            return
        def on_deleted(cat: str, replacement: str):
            self.storage.save_tasks(self.manager.get_all_tasks())
            self.rebuild_category_options()
            self.refresh_listbox("today", self.category_filter_combo.get(), self.search_entry.get().strip())
            self.log_action("Category Deleted:", f"{cat} -> {replacement}")

        DeleteCategoryDialog(self.window, self.category_manager, self.manager.get_all_tasks(), on_deleted)

    def edit_category_dialog(self) -> None:
        if not self.category_manager.get_task_categories():
            messagebox.showinfo("No Categories", "There are no user categories to rename.")
            return
        def on_renamed(old: str, new: str):
            self.storage.save_tasks(self.manager.get_all_tasks())
            self.rebuild_category_options()
            self.refresh_listbox("today", self.category_filter_combo.get(), self.search_entry.get().strip())
            self.log_action("Category Renamed:", f"{old} -> {new}")

        RenameCategoryDialog(self.window, self.category_manager, self.manager.get_all_tasks(), on_renamed)

    # ---------- Run ----------
    def run(self) -> None:
        self.window.mainloop()


