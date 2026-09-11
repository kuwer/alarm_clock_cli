from alarm_clock.clock import Clock
from alarm_clock.models import AlarmStatus
from alarm_clock.repository import AlarmRepository
from alarm_clock.scheduler import Scheduler
from alarm_clock.service import AlarmService


def test_architecture_modules_are_importable() -> None:
    assert Clock
    assert AlarmRepository
    assert Scheduler
    assert AlarmService
    assert AlarmStatus.PENDING.value == "pending"
