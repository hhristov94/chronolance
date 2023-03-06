from dataclasses import dataclass
from typing import Union
import time
from pandas import Timedelta
from datetime import datetime


@dataclass
class WorkSession:
    """A class representing a work session."""

    id: int
    name: str
    start_time: datetime
    end_time: Union[datetime, None]
    description: Union[str, None]
    limit: Union[str, None]

    def __post_init__(self):
        self.expected_end = self.start_time + Timedelta(self.limit)

    def elapsed(self) -> str:
        """Return the elapsed time formatted as HH:MM:SS."""
        return time.strftime(
            "%H:%M:%S",
            time.gmtime(
                (datetime.now() - self.start_time).total_seconds()
                if not self.end_time
                else (self.end_time - self.start_time).total_seconds()
            ),
        )

    def remaining(self) -> str:
        """Return the remaining time formatted as HH:MM:SS, with a prefix indicating whether it has expired."""
        if self.limit:
            expired = datetime.now() > self.expected_end
            prefix = "[red]" if expired else "[green]"
            seconds = (
                0 if expired else (self.expected_end - datetime.now()).total_seconds()
            )
            return prefix + time.strftime("%H:%M:%S", time.gmtime(seconds))
        return ""

    def status(self) -> str:
        """Return the status of the work session as an emoji (✅ if completed, ⌛ otherwise)."""
        return "✅" if self.end_time else "⌛"
