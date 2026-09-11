"""Alarm data model and lifecycle status definitions."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class AlarmStatus(Enum):
    PENDING = "pending"
    RINGING = "ringing"
    COMPLETED = "completed"


@dataclass
class Alarm:
    """Persisted alarm data without CLI or serialization behavior."""

    id: int
    label: str
    triggered_at: datetime
    status: AlarmStatus = AlarmStatus.PENDING
