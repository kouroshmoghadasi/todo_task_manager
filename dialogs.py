import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class _BaseDialog:
    def __init__(self, parent: tk.Tk, title: str) -> None:
        self.parent = parent
        self.dlg = tk.Toplevel(parent)
        self.dlg.title(title)
        self.dlg.resizable(False, False)
        self.dlg.transient(parent)
        self.dlg.grab_set()

    def center(self) -> None:
        try:
            self.dlg.update_idletasks()
            px = self.parent.winfo_rootx()
            py = self.parent.winfo_rooty()
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            dw = self.dlg.winfo_width()
            dh = self.dlg.winfo_height()
            x = px + max(0, (pw - dw) // 2)
            y = py + max(0, (ph - dh) // 2)
            self.dlg.geometry(f"+{x}+{y}")
        except Exception:
            pass


class AddCategoryDialog(_BaseDialog):
    def __init__(self, parent: tk.Tk, category_manager, on_added) -> None:
        super().__init__(parent, "New Category")
        self.category_manager = category_manager
        self.on_added = on_added

        frame = tk.Frame(self.dlg, bg="#f7f7f7", padx=12, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Category name", bg="#f7f7f7", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.name_var = tk.StringVar()
        name_entry = tk.Entry(frame, textvariable=self.name_var, width=28)
        name_entry.grid(row=0, column=1, sticky="w", padx=(8, 0))

        btns = tk.Frame(frame, bg="#f7f7f7")
        btns.grid(row=1, column=0, columnspan=2, sticky="e", pady=(12, 0))
        tk.Button(btns, text="Cancel", command=self._cancel, bg="#ddd", fg="#333", font=("Segoe UI", 10), width=10).pack(side="right", padx=(6, 0))
        tk.Button(btns, text="Add", command=self._ok, bg="#4CAF50", fg="white", font=("Segoe UI", 10), width=10).pack(side="right")

        name_entry.focus_set()
        self.dlg.bind("<Return>", lambda e: self._ok())
        self.dlg.bind("<Escape>", lambda e: self._cancel())
        self.center()

    def _cancel(self):
        self.dlg.destroy()

    def _ok(self):
        name = (self.name_var.get() or "").strip()
        if not name:
            return
        if name.lower() == "all" or name in self.category_manager.get_all_categories():
            messagebox.showwarning("Invalid Category", "This category is not allowed or already exists.")
            return
        if self.category_manager.add_category(name):
            if callable(self.on_added):
                self.on_added(name)
        self.dlg.destroy()


class DeleteCategoryDialog(_BaseDialog):
    def __init__(self, parent: tk.Tk, category_manager, tasks, on_deleted) -> None:
        super().__init__(parent, "Delete Category")
        self.category_manager = category_manager
        self.tasks = tasks
        self.on_deleted = on_deleted

        cats = self.category_manager.get_task_categories()
        if not cats:
            messagebox.showinfo("No Categories", "There are no user categories to delete.")
            self.dlg.destroy()
            return

        frame = tk.Frame(self.dlg, bg="#f7f7f7", padx=12, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Category to delete", bg="#f7f7f7", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.to_delete_var = tk.StringVar()
        self.to_delete_combo = ttk.Combobox(frame, textvariable=self.to_delete_var, values=cats, state="readonly", width=20)
        self.to_delete_combo.grid(row=0, column=1, sticky="w", padx=(8, 0))
        self.to_delete_combo.set(cats[0])

        tk.Label(frame, text="Reassign tasks to", bg="#f7f7f7", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.reassign_var = tk.StringVar()
        self.reassign_combo = ttk.Combobox(frame, textvariable=self.reassign_var, values=cats, state="readonly", width=20)
        self.reassign_combo.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        def sync_reassign(*_):
            options = [c for c in self.category_manager.get_task_categories() if c != self.to_delete_var.get()]
            self.reassign_combo['values'] = options
            if options:
                fallback = "Personal" if "Personal" in options else options[0]
                self.reassign_combo.set(fallback)
            else:
                self.reassign_combo.set("")

        self.to_delete_var.trace_add('write', sync_reassign)
        sync_reassign()

        btns = tk.Frame(frame, bg="#f7f7f7")
        btns.grid(row=2, column=0, columnspan=2, sticky="e", pady=(12, 0))
        tk.Button(btns, text="Cancel", command=self._cancel, bg="#ddd", fg="#333", font=("Segoe UI", 10), width=10).pack(side="right", padx=(6, 0))
        tk.Button(btns, text="Delete", command=self._delete, bg="#f44336", fg="white", font=("Segoe UI", 10), width=10).pack(side="right")

        self.center()

    def _cancel(self):
        self.dlg.destroy()

    def _delete(self):
        cat = self.to_delete_var.get()
        replacement = self.reassign_var.get()
        if not cat:
            messagebox.showwarning("Select Category", "Please select a category to delete.")
            return
        if not replacement:
            if "Personal" not in self.category_manager.get_task_categories():
                self.category_manager.add_category("Personal")
            replacement = "Personal"
        self.category_manager.delete_category(cat, replacement, self.tasks)
        if callable(self.on_deleted):
            self.on_deleted(cat, replacement)
        self.dlg.destroy()


class RenameCategoryDialog(_BaseDialog):
    def __init__(self, parent: tk.Tk, category_manager, tasks, on_renamed) -> None:
        super().__init__(parent, "Rename Category")
        self.category_manager = category_manager
        self.tasks = tasks
        self.on_renamed = on_renamed

        cats = self.category_manager.get_task_categories()
        if not cats:
            messagebox.showinfo("No Categories", "There are no user categories to rename.")
            self.dlg.destroy()
            return

        frame = tk.Frame(self.dlg, bg="#f7f7f7", padx=12, pady=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Current name", bg="#f7f7f7", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.current_var = tk.StringVar()
        current_combo = ttk.Combobox(frame, textvariable=self.current_var, values=cats, state="readonly", width=20)
        current_combo.grid(row=0, column=1, sticky="w", padx=(8, 0))
        current_combo.set(cats[0])

        tk.Label(frame, text="New name", bg="#f7f7f7", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.new_name_var = tk.StringVar()
        new_name_entry = tk.Entry(frame, textvariable=self.new_name_var, width=22)
        new_name_entry.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        btns = tk.Frame(frame, bg="#f7f7f7")
        btns.grid(row=2, column=0, columnspan=2, sticky="e", pady=(12, 0))
        tk.Button(btns, text="Cancel", command=self._cancel, bg="#ddd", fg="#333", font=("Segoe UI", 10), width=10).pack(side="right", padx=(6, 0))
        tk.Button(btns, text="Rename", command=self._rename, bg="#3F51B5", fg="white", font=("Segoe UI", 10), width=10).pack(side="right")

        new_name_entry.focus_set()
        self.dlg.bind("<Return>", lambda e: self._rename())
        self.dlg.bind("<Escape>", lambda e: self._cancel())
        self.center()

    def _cancel(self):
        self.dlg.destroy()

    def _rename(self):
        old = (self.current_var.get() or "").strip()
        new = (self.new_name_var.get() or "").strip()
        if not old:
            messagebox.showwarning("Select Category", "Please select a category to rename.")
            return
        if not new:
            messagebox.showwarning("New Name", "Please enter the new category name.")
            return
        if new.lower() == "all" or new in self.category_manager.get_all_categories():
            messagebox.showwarning("Invalid Category", "This category name is not allowed or already exists.")
            return
        self.category_manager.rename_category(old, new, self.tasks)
        if callable(self.on_renamed):
            self.on_renamed(old, new)
        self.dlg.destroy()


class EditTaskDialog(_BaseDialog):
    def __init__(self, parent: tk.Tk, task, category_manager, on_saved) -> None:
        super().__init__(parent, "Edit Task")
        self.task = task
        self.category_manager = category_manager
        self.on_saved = on_saved

        content = tk.Frame(self.dlg, bg="#f7f7f7", padx=12, pady=10)
        content.pack(fill="both", expand=True)

        tk.Label(content, text="Title", bg="#f7f7f7", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar(value=task.title)
        title_entry = tk.Entry(content, textvariable=self.title_var, width=40, font=("Segoe UI", 11))
        title_entry.grid(row=0, column=1, sticky="w", padx=(8, 0))

        tk.Label(content, text="Category", bg="#f7f7f7", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w", pady=(8, 0))
        category_values = self.category_manager.get_task_categories()
        if task.category not in category_values:
            category_values = category_values + [task.category]
        self.category_var = tk.StringVar(value=task.category)
        category_combo_local = ttk.Combobox(content, textvariable=self.category_var, values=category_values,
                                            state="readonly", width=18, font=("Segoe UI", 11))
        category_combo_local.grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        self.completed_var = tk.BooleanVar(value=task.completed)
        completed_check = tk.Checkbutton(content, text="Completed", variable=self.completed_var, onvalue=True,
                                         offvalue=False, bg="#f7f7f7", font=("Segoe UI", 10))
        completed_check.grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(8, 0))

        meta_frame = tk.Frame(content, bg="#f7f7f7")
        meta_frame.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))
        try:
            created = f"{task.created_at.split('T')[0]} {task.created_at.split('T')[1][:8]}"
        except Exception:
            created = task.created_at
        done = "-"
        try:
            if task.done_at:
                done = f"{task.done_at.split('T')[0]} {task.done_at.split('T')[1][:8]}"
        except Exception:
            pass
        tk.Label(meta_frame, text=f"Created: {created}", bg="#f7f7f7", fg="#666", font=("Segoe UI", 9)).pack(anchor="w")
        tk.Label(meta_frame, text=f"Done: {done}", bg="#f7f7f7", fg="#666", font=("Segoe UI", 9)).pack(anchor="w")

        btns = tk.Frame(content, bg="#f7f7f7")
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(12, 0))
        tk.Button(btns, text="Cancel", command=self._cancel, bg="#ddd", fg="#333", font=("Segoe UI", 10), width=10).pack(side="right", padx=(6, 0))
        tk.Button(btns, text="Save", command=self._save, bg="#4CAF50", fg="white", font=("Segoe UI", 10), width=10).pack(side="right")

        self.dlg.bind("<Return>", lambda e: self._save())
        self.dlg.bind("<Escape>", lambda e: self._cancel())
        self.center()
        title_entry.focus_set()

    def _cancel(self):
        self.dlg.destroy()

    def _save(self):
        new_title = (self.title_var.get() or "").strip()
        if not new_title:
            messagebox.showwarning("Empty Title", "Please enter a title.")
            return
        new_category = self.category_var.get()
        new_completed = self.completed_var.get()

        changed = False
        if self.task.title != new_title:
            self.task.title = new_title
            changed = True
        if self.task.category != new_category:
            self.task.category = new_category
            changed = True
        if new_completed and not self.task.completed:
            self.task.completed = True
            self.task.done_at = datetime.now().isoformat()
            changed = True
        elif not new_completed and self.task.completed:
            self.task.completed = False
            self.task.done_at = None
            changed = True

        if changed and callable(self.on_saved):
            self.on_saved(self.task)
        self.dlg.destroy()


