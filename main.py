import tkinter as tk
from tkinter import messagebox, filedialog
from task import Task
from task_manager import TaskManager
from task_storage import TaskStorage
from datetime import datetime
from tkcalendar import DateEntry
# import csv
from task_exporter import TaskExporter


# =========================

exporter = TaskExporter()

# =========================
# Initialization
storage = TaskStorage()
manager = TaskManager()
manager.tasks = storage.load_tasks()

# =========================
# Functions
def refresh_listbox(date_filter=None):
    task_listbox.delete(0, tk.END)
    tasks = filter_tasks(date_filter)
    for task in tasks:
        display = f"✔️ {task.title}" if task.completed else task.title
        task_listbox.insert(tk.END, display)
    global last_filter
    last_filter = date_filter  # store last used filter

def filter_tasks(date_filter):
    """Return tasks filtered by date."""
    tasks = manager.get_all_tasks()
    if date_filter == "today":
        today = datetime.now().strftime("%Y-%m-%d")
        return [t for t in tasks if t.created_at.split("T")[0] == today]
    elif isinstance(date_filter, str):
        return [t for t in tasks if t.created_at.split("T")[0] == date_filter]
    return tasks

def current_filter():
    """Return the current active date filter."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    selected_date = date_picker.get_date().strftime("%Y-%m-%d")
    if selected_date == today_str:
        return "today"
    return selected_date

def add_task():
    title = entry.get().strip()
    if not title:
        messagebox.showwarning("Empty Task", "Please enter a task.")
        return
    manager.add_task(title)
    storage.save_tasks(manager.get_all_tasks())
    entry.delete(0, tk.END)
    refresh_listbox("today")

def delete_task():
    selected = task_listbox.curselection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a task to delete.")
        return
    tasks = filter_tasks(last_filter)
    index = selected[0]
    task = tasks[index]
    manager.delete_task(task.id)
    storage.save_tasks(manager.get_all_tasks())
    refresh_listbox(last_filter)

def mark_done():
    selected = task_listbox.curselection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a task to mark as done.")
        return
    tasks = filter_tasks(last_filter)
    index = selected[0]
    task = tasks[index]
    manager.mark_task_done(task.id)
    storage.save_tasks(manager.get_all_tasks())
    refresh_listbox(last_filter)

def today_tasks():
    refresh_listbox("today")

def filter_by_date():
    selected_date = date_picker.get_date().strftime("%Y-%m-%d")
    refresh_listbox(selected_date)

def export_to_csv():
    tasks = filter_tasks(last_filter)
    exporter.export_to_csv(tasks)

# =========================
# UI Setup
window = tk.Tk()
window.title("To-Do Task Manager")
window.resizable(False, False)
window.configure(bg="#f0f0f0")

# Close on Esc key
window.bind("<Escape>", lambda e: window.destroy())

# Center window
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
win_width = 900
win_height = 600
x = int((screen_width - win_width) / 2)
y = int((screen_height - win_height) / 2)
window.geometry(f"{win_width}x{win_height}+{x}+{y}")

# Main layout
main_frame = tk.Frame(window, bg="#f0f0f0")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Left - Buttons
button_frame = tk.LabelFrame(main_frame, text="Actions", bg="#e0e0e0", font=("Segoe UI", 11, "bold"), relief="ridge", borderwidth=4)
button_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=5)

tk.Button(button_frame, text="Add Task", width=20, command=add_task,
          bg="#4CAF50", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Delete Task", width=20, command=delete_task,
          bg="#f44336", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Mark as Done", width=20, command=mark_done,
          bg="#2196F3", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Show All Tasks", width=20, command=lambda: refresh_listbox(None),
          bg="#218071", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Today's tasks", width=20, command=today_tasks,
          bg="#622180", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Export to CSV", width=20, command=export_to_csv,
          bg="#FF9800", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

# Right - Input, Date, Listbox
right_frame = tk.Frame(main_frame, bg="#f0f0f0")
right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
right_frame.columnconfigure(0, weight=1)

input_frame = tk.Frame(right_frame, bg="#f0f0f0")
input_frame.pack(fill="x", pady=(0, 5))

entry = tk.Entry(input_frame, width=40, font=("Segoe UI", 12))
entry.pack(side="left", padx=(0, 5))

date_picker = DateEntry(input_frame, width=18, font=("Segoe UI", 11), date_pattern='yyyy-mm-dd')
date_picker.pack(side="left", padx=(0, 5))

tk.Button(input_frame, text="Filter", command=filter_by_date,
          bg="#555", fg="white", font=("Segoe UI", 11)).pack(side="left")

task_listbox = tk.Listbox(right_frame, width=50, height=20, font=("Segoe UI", 12))
task_listbox.pack(fill="both", expand=True)

# =========================
# Load today's tasks at startup
last_filter = "today"
refresh_listbox("today")

window.mainloop()
