"""Command-line entry point and terminal interaction boundary."""

import argparse
from pathlib import Path
from datetime import datetime

from .clock import Clock
from .repository import AlarmRepository, PersistenceError
from .scheduler import Scheduler
from .service import AlarmService


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    repository = AlarmRepository(Path("data/alarms.json"))
    service = AlarmService(repository)

    try:
        if args.command == "set":
            alarm = service.set_alarm(args.time, args.label)
            print(f"Created alarm {alarm.id} for {alarm.triggered_at:%Y-%m-%d %H:%M}")
        elif args.command == "list":
            for alarm in service.list_alarms():
                print(f"{alarm.id}: {alarm.triggered_at:%Y-%m-%d %H:%M} [{alarm.status.value}] {alarm.label}")
        elif args.command == "delete":
            service.delete_alarm(args.id)
            print(f"Deleted alarm {args.id}")
        elif args.command == "run":
            Scheduler(service, repository, Clock().now).run()
    except (ValueError, KeyError, PersistenceError) as error:
        parser.error(str(error))
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="alarm")
    commands = parser.add_subparsers(dest="command", required=True)

    set_command = commands.add_parser("set")
    set_command.add_argument("time", help="alarm time in HH:MM format")
    set_command.add_argument("--label", default="Alarm")

    commands.add_parser("list")

    delete_command = commands.add_parser("delete")
    delete_command.add_argument("id", type=int)

    commands.add_parser("run")
    return parser
