"""Long-running polling scheduler."""

import time
from collections.abc import Callable
from datetime import datetime

from .models import Alarm, AlarmStatus
from .repository import AlarmRepository
from .service import AlarmService


class Scheduler:
    """Poll persisted alarms and handle ringing alarms one at a time."""

    def __init__(
        self,
        service: AlarmService,
        repository: AlarmRepository,
        now: Callable[[], datetime],
        input_fn: Callable[[str], str] = input,
        output: Callable[[str], None] = print,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.service = service
        self.repository = repository
        self.now = now
        self.input = input_fn
        self.output = output
        self.sleep = sleep

    def run_once(self) -> bool:
        alarms = self.repository.get_all()
        current_time = self.now()
        due = [
            alarm
            for alarm in alarms
            if alarm.status == AlarmStatus.RINGING
            or (alarm.status == AlarmStatus.PENDING and alarm.triggered_at <= current_time)
        ]
        due.sort(key=lambda alarm: (alarm.triggered_at, alarm.id))

        for alarm in due:
            if alarm.status == AlarmStatus.PENDING:
                alarm.status = AlarmStatus.RINGING
                self.repository.update(alarm)
            self._handle_ringing(alarm)
        return bool(due)

    def run(self) -> None:
        while True:
            self.run_once()
            self.sleep(1)

    def _handle_ringing(self, alarm: Alarm) -> None:
        self.output(f"Alarm {alarm.id}: {alarm.label}")
        print("\a", end="", flush=True)
        while True:
            action = self.input("stop or snooze? ").strip().lower()
            if action == "stop":
                self.service.stop(alarm)
                return
            if action == "snooze":
                self.service.snooze(alarm)
                return
            self.output("Please enter 'stop' or 'snooze'.")
