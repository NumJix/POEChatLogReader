import tkinter as tk
from tkinter import messagebox

from log_watcher.log_watcher_gui import LogWatcherGUI


# Check if the GUI is already running
def is_running():
    # You can implement a check for existing GUI instances here.
    # For now, this is just a placeholder for your logic.
    return False


if __name__ == '__main__':
    if is_running():
        messagebox.showwarning("Warning", "Application is already running.")
    else:
        root = tk.Tk()
        app = LogWatcherGUI(root, max_logs=100)
        root.mainloop()
