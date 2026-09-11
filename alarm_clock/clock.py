"""Current local time provider."""

from datetime import datetime


class Clock:
    """Provides the current local system time."""

    def now(self) -> datetime:
        return datetime.now().astimezone()
