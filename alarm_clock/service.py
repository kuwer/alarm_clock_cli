"""Application operations for alarm use cases."""

from datetime import datetime, time, timedelta

from .clock import Clock
from .models import Alarm, AlarmStatus
from .repository import AlarmRepository


class AlarmService:
    """Coordinate alarm creation and lifecycle updates with the repository."""

    def __init__(self, repository: AlarmRepository, clock: Clock | None = None) -> None:
        self.repository = repository
        self.clock = clock or Clock()

    def set_alarm(self, time_text: str, label: str) -> Alarm:
        now = self.clock.now()
        try:
            alarm_time = datetime.strptime(time_text, "%H:%M").time()
        except ValueError as error:
            raise ValueError("time must use HH:MM format") from error

        triggered_at = datetime.combine(now.date(), alarm_time, tzinfo=now.tzinfo)
        if triggered_at <= now:
            triggered_at += timedelta(days=1)

        alarms = self.repository.get_all()
        next_id = max((alarm.id for alarm in alarms), default=0) + 1
        alarm = Alarm(next_id, label, triggered_at)
        self.repository.add(alarm)
        return alarm

    def list_alarms(self) -> list[Alarm]:
        return self.repository.get_all()

    def delete_alarm(self, alarm_id: int) -> None:
        self.repository.delete(alarm_id)

    def stop(self, alarm: Alarm) -> Alarm:
        alarm.status = AlarmStatus.COMPLETED
        self.repository.update(alarm)
        return alarm

    def snooze(self, alarm: Alarm) -> Alarm:
        alarm.triggered_at = self.clock.now() + timedelta(minutes=5)
        alarm.status = AlarmStatus.PENDING
        self.repository.update(alarm)
        return alarm
