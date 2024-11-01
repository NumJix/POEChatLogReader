import os
import time

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from threading import Thread
from watchdog.observers import Observer

from log_watcher.log_watcher import LogWatcher
from models.chat_groups import ChatGroup
from models.poe_logs import POELogs

from py_config.about import about_text
from py_config.help import help_text


class LogWatcherGUI:
    def __init__(self, root, max_logs):
        self.root = root
        self.root.title('POE Chat Log Watcher')

        # Create a frame to hold the log file selection UI
        self.file_selection_frame = ttk.Frame(self.root)
        self.file_selection_frame.pack(pady=10, padx=10, fill='x')

        # Create a Label to display the selected log file path
        self.selected_file_label = tk.Label(self.file_selection_frame,
                                            text='No file selected',
                                            anchor='w')
        self.selected_file_label.pack(side='left', fill='x', expand=True)

        # Create a button to open the file picker
        self.select_file_button = ttk.Button(self.file_selection_frame,
                                             text='Select Log File',
                                             command=self.select_log_file)
        self.select_file_button.pack(side='right')

        # Create a notebook (tabs container)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Initialize chat group
        self.chat_group = ChatGroup(max_logs=max_logs)

        # Create a dictionary to hold the Treeview for each tab
        self.treeviews = {
            'global_': self.create_tab('Global'),
            'party': self.create_tab('Party'),
            'whisper': self.create_tab('Whisper'),
            'trade': self.create_tab('Trade'),
            'guild': self.create_tab('Guild')
        }

        # Create a label for displaying messages
        self.message_label = tk.Label(self.root, text='', fg='green')
        self.message_label.pack(pady=5)

        # Bind keyboard shortcuts for copying text
        self.root.bind('<Control-c>', self.copy_selection)

        # Add a refresh button
        self.refresh_button = ttk.Button(self.root, text='Refresh Logs',
                                         command=self.refresh_logs)
        self.refresh_button.pack(pady=10)

        # Add an About button
        self.about_button = ttk.Button(self.root, text='About',
                                       command=self.show_about)
        self.about_button.pack(side='left', padx=(10, 0))

        # Add a Help button
        self.help_button = ttk.Button(self.root, text='Help',
                                      command=self.show_help)
        self.help_button.pack(side='left', padx=(10, 0))

    def show_help(self):
        '''Displays a Help message box.'''
        messagebox.showinfo('Help', help_text)

    def select_log_file(self):
        '''Opens a file picker dialog to select the log file.'''
        log_file_path = filedialog.askopenfilename(
            title='Select Log File',
            filetypes=(('Text Files', '*.txt'), ('All Files', '*.*'))
        )

        if log_file_path:  # Check if a file was selected
            # Validate file extension
            if not log_file_path.lower().endswith('.txt'):
                messagebox.showerror('Invalid File Type',
                                     'Please select a valid .txt log file.')
                return

            self.selected_file_label.config(text=log_file_path)
            self.log_watcher = LogWatcher(log_file_path, self.chat_group)
            self.populate_treeviews()
            self.start_watcher()

    def start_watcher(self):
        '''Starts the log watcher in a separate thread.'''
        self.watcher_thread = Thread(target=self.run_watcher, daemon=True)
        self.watcher_thread.start()

    def show_about(self):
        '''Displays an About message box.'''
        messagebox.showinfo('About POE chat reader', about_text)

    def copy_cell(self, cell_value):
        '''Copies the specific cell value to the
        clipboard and shows a message.'''
        if cell_value:
            self.root.clipboard_clear()
            self.root.clipboard_append(str(cell_value))
            self.show_message(f'"{str(cell_value)}" Copied to clipboard.')
        else:
            self.show_message('Please select a valid cell to copy.', 'red')

    def show_message(self, message, color='green'):
        '''Displays a temporary message in the message label.'''
        self.message_label.config(text=message, fg=color)
        self.root.after(3000, self.clear_message)  # Clear the message after 3s

    def clear_message(self):
        '''Clears the message label.'''
        self.message_label.config(text='')

    def create_tab(self, title):
        '''Creates a new tab with a Treeview and a
        vertical scrollbar for log display.'''
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)

        # Create a Treeview for displaying logs
        treeview = ttk.Treeview(frame,
                                columns=('date_time', 'group', 'guild',
                                         'username', 'message'),
                                show='headings')
        treeview.heading('date_time', text='DateTime')
        treeview.heading('group', text='Group')
        treeview.heading('guild', text='Guild')
        treeview.heading('username', text='Username')
        treeview.heading('message', text='Message')
        treeview.column('date_time', width=150)
        treeview.column('group', width=50)
        treeview.column('guild', width=75)
        treeview.column('username', width=150)
        treeview.column('message', width=300)

        # Create a vertical scrollbar and associate it with the Treeview
        v_scrollbar = ttk.Scrollbar(frame, orient="vertical",
                                    command=treeview.yview)
        treeview.configure(yscrollcommand=v_scrollbar.set)

        # Pack the Treeview and scrollbar
        treeview.pack(side='left', expand=True, fill='both', padx=5, pady=5)
        v_scrollbar.pack(side='right', fill='y')

        # Bind right-click for context menu
        treeview.bind('<Button-3>', self.show_context_menu)

        return treeview

    def show_context_menu(self, event):
        '''Displays a context menu to copy selected cell.'''
        treeview = event.widget
        row_id = treeview.identify_row(event.y)
        column_id = treeview.identify_column(event.x)

        if row_id and column_id:
            # Clear previous highlights
            self.clear_highlight(treeview)

            # Get the value of the clicked cell
            column = column_id.replace('#', '')  # Convert to column index
            item_values = treeview.item(row_id)['values']
            cell_value = item_values[int(column) - 1]

            # Highlight the clicked cell
            self.highlight_cell(treeview, row_id, int(column))

            # Create a context menu
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label='Copy',
                             command=lambda: self.copy_cell(cell_value))
            menu.post(event.x_root, event.y_root)

    def highlight_cell(self, treeview, row_id, column_index):
        '''Highlights a specific cell in the Treeview.'''
        treeview.tag_configure('highlight', background='lightblue')
        treeview.item(row_id, tags=('highlight',))

    def clear_highlight(self, treeview):
        '''Clears all highlights in the Treeview.'''
        for item in treeview.get_children():
            treeview.item(item, tags=())  # Remove all tags from items

    def copy_selection(self, event=None):
        '''Copies the selected log entry to the clipboard.'''
        for treeview in self.treeviews.values():
            selected_item = treeview.selection()
            if selected_item:
                item_values = treeview.item(selected_item)['values']
                text_to_copy = '\t'.join(map(str, item_values))
                self.root.clipboard_clear()
                self.root.clipboard_append(text_to_copy)
                messagebox.showinfo('Copied', 'Log entry copied to clipboard.')
                return
        messagebox.showwarning('No Selection',
                               'Please select a log entry to copy.')

    def run_watcher(self):
        '''Starts the Observer to watch for file changes.'''
        observer = Observer()
        observer.schedule(self.log_watcher,
                          path=os.path.dirname(self.log_watcher.log_file_path),
                          recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)  # Keep thread alive
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def refresh_logs(self):
        '''Manually refreshes the logs in the UI.'''
        for category in self.treeviews:
            logs: list[POELogs] = getattr(self.chat_group, category, [])
            treeview = self.treeviews[category]

            # Clear existing items in the Treeview
            treeview.delete(*treeview.get_children())

            # Insert new logs into the Treeview
            for log in logs:
                treeview.insert('', 'end', values=(
                    log.date_time.strftime('%Y/%m/%d %H:%M:%S'),
                    log.group,
                    log.guild,
                    log.username,
                    log.message))
            treeview.yview_moveto(1.0)

    def populate_treeviews(self):
        '''Populates the Treeviews with existing
        logs when the application starts.'''
        for category in self.treeviews:
            logs: list[POELogs] = getattr(self.chat_group, category, [])
            treeview = self.treeviews[category]

            # Insert logs into the Treeview
            for log in logs:
                treeview.insert('', 'end', values=(
                    log.date_time.strftime('%Y/%m/%d %H:%M:%S'),
                    log.group,
                    log.guild,
                    log.username,
                    log.message))
            # Move to bottom
            treeview.yview_moveto(1.0)
