from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime as dt


class POELogs(BaseModel):
    group: str
    guild: Optional[str] = Field(default='')
    username: str
    message: str
    date_time: dt
