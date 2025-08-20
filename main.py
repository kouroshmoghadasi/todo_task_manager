import tkinter as tk
from tkinter import messagebox
from task import Task
from task_manager import TaskManager
from task_storage import TaskStorage
from datetime import datetime
from tkcalendar import DateEntry
import csv
import winsound   # برای Beep

# =========================
# مقداردهی اولیه
storage = TaskStorage()
manager = TaskManager()
manager.tasks = storage.load_tasks()

LOG_FILE = "activity.log"
current_tasks = []  # لیست تسک‌های نمایش داده شده

# =========================
# توابع کمکی
def log_action(action, task_title=""):
    """ثبت فعالیت در فایل لاگ"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action} {task_title}\n")

def play_beep():
    """پخش صدای بیپ کوتاه"""
    winsound.Beep(1000, 200)

# =========================
# توابع اصلی
def refresh_listbox(date_filter=None):
    global current_tasks
    task_listbox.delete(0, tk.END)
    tasks = manager.get_all_tasks()

    if date_filter == "today":
        today = datetime.now().strftime("%Y-%m-%d")
        tasks = [t for t in tasks if t.created_at.split("T")[0] == today]
    elif isinstance(date_filter, str):
        tasks = [t for t in tasks if t.created_at.split("T")[0] == date_filter]

    current_tasks = tasks  # ذخیره لیست جاری برای هماهنگی ایندکس‌ها

    for task in tasks:
        display = f"✔️ {task.title}" if task.completed else task.title
        task_listbox.insert(tk.END, display)

def add_task():
    title = entry.get().strip()
    if not title:
        messagebox.showwarning("Empty Task", "Please enter a task.")
        return
    manager.add_task(title)
    storage.save_tasks(manager.get_all_tasks())
    entry.delete(0, tk.END)
    refresh_listbox("today")
    log_action("Task Added:", title)
    play_beep()

def delete_task():
    selected = task_listbox.curselection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a task to delete.")
        return
    index = selected[0]
    task = current_tasks[index]   # از لیست فیلترشده برداشته میشه
    manager.delete_task(task.id)
    storage.save_tasks(manager.get_all_tasks())
    refresh_listbox("today")
    log_action("Task Deleted:", task.title)

def mark_done():
    selected = task_listbox.curselection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a task to mark as done.")
        return
    index = selected[0]
    task = current_tasks[index]   # از لیست فیلترشده برداشته میشه
    manager.mark_task_done(task.id)
    storage.save_tasks(manager.get_all_tasks())
    refresh_listbox("today")
    log_action("Task Completed:", task.title)
    play_beep()

def today_tasks():
    refresh_listbox("today")
    log_action("Filter:", "Today")

def filter_by_date():
    selected_date = date_picker.get_date().strftime("%Y-%m-%d")
    refresh_listbox(selected_date)
    log_action("Filter by Date:", selected_date)

def show_all_tasks():
    refresh_listbox(None)
    log_action("Filter:", "All Tasks")

def export_to_csv():
    filename = f"tasks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Title", "Completed", "Created At", "Done At"])
        for task in manager.get_all_tasks():
            writer.writerow([task.id, task.title, task.completed, task.created_at, task.done_at])
    messagebox.showinfo("Exported", f"Tasks exported to {filename}")
    log_action("Tasks Exported:", filename)

# =========================
# رابط گرافیکی
window = tk.Tk()
window.title("To-Do Task Manager")
window.resizable(False, False)
window.configure(bg="#f0f0f0")

# کلید ESC برای بستن برنامه
window.bind("<Escape>", lambda e: window.destroy())

# مرکز‌چین کردن پنجره
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
win_width = 900
win_height = 600
x = int((screen_width - win_width) / 2)
y = int((screen_height - win_height) / 2)
window.geometry(f"{win_width}x{win_height}+{x}+{y}")

# =========================
# ساخت دو ستون
main_frame = tk.Frame(window, bg="#f0f0f0")
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# ستون چپ - دکمه‌ها
button_frame = tk.LabelFrame(main_frame, text="Actions", bg="#e0e0e0",
                             font=("Segoe UI", 11, "bold"), relief="ridge", borderwidth=4)
button_frame.grid(row=0, column=0, sticky="ns", padx=10, pady=5)

tk.Button(button_frame, text="Add Task", width=20, command=add_task,
          bg="#4CAF50", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Delete Task", width=20, command=delete_task,
          bg="#f44336", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Mark as Done", width=20, command=mark_done,
          bg="#2196F3", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Show All Tasks", width=20, command=show_all_tasks,
          bg="#218071", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Today's Tasks", width=20, command=today_tasks,
          bg="#622180", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

tk.Button(button_frame, text="Export to CSV", width=20, command=export_to_csv,
          bg="#ff9800", fg="white", font=("Segoe UI", 11)).pack(pady=4, padx=8)

# ستون راست - ورودی، تاریخ، لیست
right_frame = tk.Frame(main_frame, bg="#f0f0f0")
right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
right_frame.columnconfigure(0, weight=1)

# فیلد ورودی و انتخاب تاریخ در یک ردیف
input_frame = tk.Frame(right_frame, bg="#f0f0f0")
input_frame.pack(fill="x", pady=(0, 5))

entry = tk.Entry(input_frame, width=40, font=("Segoe UI", 12))
entry.pack(side="left", padx=(0, 5))

date_picker = DateEntry(input_frame, width=18, font=("Segoe UI", 11), date_pattern='yyyy-mm-dd')
date_picker.pack(side="left", padx=(0, 5))

tk.Button(input_frame, text="Filter", command=filter_by_date,
          bg="#555", fg="white", font=("Segoe UI", 11)).pack(side="left")

# لیست تسک‌ها
task_listbox = tk.Listbox(right_frame, width=50, height=20, font=("Segoe UI", 12))
task_listbox.pack(fill="both", expand=True)

# =========================
# بارگذاری اولیه
refresh_listbox("today")

window.mainloop()
