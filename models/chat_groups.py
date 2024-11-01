from pydantic import BaseModel, Field, model_validator
from models.poe_logs import POELogs
from typing import Optional, List


class ChatGroup(BaseModel):
    global_: Optional[List[POELogs]] = Field(default=[])
    party: Optional[List[POELogs]] = Field(default=[])
    whisper: Optional[List[POELogs]] = Field(default=[])
    trade: Optional[List[POELogs]] = Field(default=[])
    guild: Optional[List[POELogs]] = Field(default=[])
    max_logs: Optional[int] = None  # Maximum logs to keep in each category

    @model_validator(mode='before')
    def apply_max_logs(cls, values):
        '''Initialize lists with the max_logs constraint if max_logs is set.'''
        max_logs = values.get('max_logs')
        if max_logs:
            values['global_'] = values.get('global_', [])[-max_logs:]
            values['party'] = values.get('party', [])[-max_logs:]
            values['whisper'] = values.get('whisper', [])[-max_logs:]
            values['trade'] = values.get('trade', [])[-max_logs:]
            values['guild'] = values.get('guild', [])[-max_logs:]
        return values

    def add_log(self, log: POELogs):
        '''Categorize and add log to the appropriate list,
        enforcing max_logs if set.'''
        category = None
        if log.group == '#':
            category = 'global_'
        elif log.group == '%':
            category = 'party'
        elif log.group in ['@To', '@From']:
            category = 'whisper'
        elif log.group == '$':
            category = 'trade'
        elif log.group == '&':
            category = 'guild'

        if category:
            logs = getattr(self, category, [])
            logs.append(log)

            # Enforce the max_logs constraint
            if self.max_logs and len(logs) > self.max_logs:
                setattr(self, category, logs[-self.max_logs:])
            else:
                setattr(self, category, logs)
