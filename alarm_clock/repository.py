"""JSON persistence boundary for alarms."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import Alarm, AlarmStatus


class PersistenceError(Exception):
    """Raised when the alarm persistence file is not valid alarm data."""


class AlarmRepository:
    """Store alarms as JSON in the local persistence file."""

    def __init__(self, path: Path = Path("data/alarms.json")) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> list[Alarm]:
        if not self.path.exists():
            return []

        try:
            with self.path.open("r", encoding="utf-8") as file:
                records = json.load(file)
            if not isinstance(records, list):
                raise ValueError("root value must be a list")
            return [self._from_record(record) for record in records]
        except (json.JSONDecodeError, OSError, TypeError, ValueError, KeyError) as error:
            raise PersistenceError(f"Invalid alarm persistence file: {self.path}") from error

    def save(self, alarms: list[Alarm]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as file:
            json.dump([self._to_record(alarm) for alarm in alarms], file, indent=2)
            file.write("\n")

    def get_all(self) -> list[Alarm]:
        return self.load()

    def add(self, alarm: Alarm) -> None:
        alarms = self.load()
        alarms.append(alarm)
        self.save(alarms)

    def update(self, alarm: Alarm) -> None:
        alarms = self.load()
        for index, current in enumerate(alarms):
            if current.id == alarm.id:
                alarms[index] = alarm
                self.save(alarms)
                return
        raise KeyError(f"Alarm not found: {alarm.id}")

    def delete(self, alarm_id: int) -> None:
        alarms = self.load()
        remaining = [alarm for alarm in alarms if alarm.id != alarm_id]
        if len(remaining) == len(alarms):
            raise KeyError(f"Alarm not found: {alarm_id}")
        self.save(remaining)

    @staticmethod
    def _to_record(alarm: Alarm) -> dict[str, Any]:
        return {
            "id": alarm.id,
            "label": alarm.label,
            "triggered_at": alarm.triggered_at.isoformat(),
            "status": alarm.status.value,
        }

    @staticmethod
    def _from_record(record: Any) -> Alarm:
        if not isinstance(record, dict):
            raise ValueError("alarm record must be an object")

        alarm_id = record["id"]
        label = record["label"]
        triggered_at = record["triggered_at"]
        status = record["status"]
        if isinstance(alarm_id, bool) or not isinstance(alarm_id, int):
            raise ValueError("alarm id must be an integer")
        if not isinstance(label, str) or not isinstance(triggered_at, str):
            raise ValueError("alarm label and triggered_at must be strings")

        return Alarm(
            id=alarm_id,
            label=label,
            triggered_at=datetime.fromisoformat(triggered_at),
            status=AlarmStatus(status),
        )
