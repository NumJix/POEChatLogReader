import re
import os
from datetime import datetime as dt

from dotenv import load_dotenv

from models.poe_logs import POELogs


load_dotenv()


def extract_details_from_logs(log_line):
    pattern = os.environ['EXTRACT_REGEX']
    match = re.search(pattern, log_line)

    if match:
        date_time = dt.strptime(f"{match.group(1)} {match.group(2)}",
                                "%Y/%m/%d %H:%M:%S")
        group = match.group(3)
        guild = match.group(4) if match.group(4) else ''
        user = match.group(5)
        message = match.group(6)
        return group, guild, user, message, date_time


def resolve_log_to_object(extract):
    group, guild, username, message, date_time = extract
    return POELogs(group=group,
                   guild=guild,
                   username=username,
                   message=message,
                   date_time=date_time)
