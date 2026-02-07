import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os, shutil, mimetypes
import logging
from classifier import classify_files
from aisort import sort_by_content

# ---------- LOGGING SETUP ----------

# Handler to write logs into a Tkinter Text widget
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record) + '\n'
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg)
        self.text_widget.configure(state='disabled')
        self.text_widget.see(tk.END)

# ---------- GUI Event Handlers ----------

def sort_files(mode, path, status_var):
    logging.info(f"🔄 Starting sort | mode={mode.get()} | path={path}")
    status_var.set("Sorting...")
    try:
        if mode.get() == "type":
            logging.info("📂 Sorting by file type")
            classify_files(path)
        else:
            logging.info("📝 Sorting by file content")
            sort_by_content(path)
        status_var.set("Sorting Completed ✅")
        logging.info("✅ Sorting completed without errors")
    except Exception as e:
        status_var.set(f"Sorting Error ❌: {str(e)}")
        logging.error(f"❌ Sorting error: {e}", exc_info=True)

def start_sorting(mode, path_entry, status_var):
    folder_path = path_entry.get()
    if not folder_path:
        messagebox.showwarning("No Folder", "Please select a folder.")
        return
    threading.Thread(
        target=sort_files,
        args=(mode, folder_path, status_var),
        daemon=True
    ).start()

def browse_folder(entry_widget):
    folder_path = filedialog.askdirectory()
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, folder_path)


# ---------- GUI Setup ----------

root = tk.Tk()
root.title("AI File Sorter")

# Source folder selection
tk.Label(root, text="Select Folder:").pack(pady=5)
path_entry = tk.Entry(root, width=50)
path_entry.pack(side=tk.LEFT, padx=10)
tk.Button(root, text="Browse", command=lambda: browse_folder(path_entry)).pack(side=tk.LEFT)

# Mode selection
mode = tk.StringVar(value="type")
tk.Radiobutton(root, text="Sort by File Type",   variable=mode, value="type").pack(anchor="w")
tk.Radiobutton(root, text="Sort by File Content", variable=mode, value="content").pack(anchor="w")

# Sort button & status
status_var = tk.StringVar(value="Waiting...")
tk.Button(root, text="Sort", command=lambda: start_sorting(mode, path_entry, status_var)).pack(pady=10)
tk.Label(root, textvariable=status_var, fg="blue").pack(pady=5)

# ---------- LOGS DISPLAY ----------

log_box = tk.Text(root, height=10, state="disabled", bg="#f0f0f0")
log_box.pack(fill="both", expand=True, padx=5, pady=(0,10))

# Configure root logger to use our TextHandler
handler = TextHandler(log_box)
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%H:%M:%S"))
logging.getLogger().addHandler(handler)
logging.getLogger().setLevel(logging.INFO)

root.mainloop()