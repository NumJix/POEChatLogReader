from models.chat_groups import ChatGroup
from watchdog.events import FileSystemEventHandler
from utils.read_logs import extract_details_from_logs, resolve_log_to_object


class LogWatcher(FileSystemEventHandler):
    def __init__(self, log_file_path, chat_group: ChatGroup):
        self.log_file_path = log_file_path
        self.chat_group = chat_group
        self.last_position = 0
        self.read_existing_logs()  # Initial read of existing log content

    def read_existing_logs(self):
        '''Reads the entire log file up to the end to
        capture any existing log entries.'''
        with open(self.log_file_path, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
            self.last_position = f.tell()  # Set position - end of the file

            for line in existing_lines:
                extract = extract_details_from_logs(line)
                if extract:
                    log = resolve_log_to_object(extract)
                    self.chat_group.add_log(log)

    def on_modified(self, event):
        # Only respond to changes in the log file
        if event.src_path == self.log_file_path:
            self.read_new_lines()

    def read_new_lines(self):
        '''Reads only new lines added to the file since last read.'''
        with open(self.log_file_path, 'r') as f:
            f.seek(self.last_position)
            new_lines = f.readlines()
            self.last_position = f.tell()

            # Parse and categorize new lines
            for line in new_lines:
                extract = extract_details_from_logs(line)
                if extract:
                    log = resolve_log_to_object(extract)
                    self.chat_group.add_log(log)
