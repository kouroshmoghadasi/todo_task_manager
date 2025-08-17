import csv
from tkinter import filedialog, messagebox

class TaskExporter:
    def __init__(self):
        pass

    def export_to_csv(self, tasks):
        """
        Exports a list of Task objects to CSV.
        Each task should have: id, title, completed, created_at, done_at
        """
        if not tasks:
            messagebox.showwarning("No Data", "No tasks available to export.")
            return

        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            title="Save Tasks As"
        )
        if not file_path:
            return  # Cancelled

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Title", "Completed", "Created At", "Done At"])
                for task in tasks:
                    writer.writerow([
                        task.id,
                        task.title,
                        "Yes" if task.completed else "No",
                        task.created_at,
                        task.done_at or ""
                    ])
            messagebox.showinfo("Export Successful", f"Tasks exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred:\n{e}")
