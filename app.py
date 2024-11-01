import tkinter as tk

from log_watcher.log_watcher_gui import LogWatcherGUI


# Run the application
if __name__ == '__main__':
    max_logs = 100

    root = tk.Tk()
    app = LogWatcherGUI(root, max_logs)
    root.mainloop()
