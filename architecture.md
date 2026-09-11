# Alarm Clock CLI Architecture

## Goal

Provide the smallest architecture that supports setting, listing, deleting, triggering, snoozing, stopping, persistence, and scheduler recovery within a 30-45 minute implementation.

## Components

### CLI Commands

**Responsibilities**

- Parse `set`, `list`, `delete`, and `run` commands.
- Validate command input.
- Call application operations.
- Render results and errors for the terminal.
- Print alarm notifications and read `stop` or `snooze` responses during `run`.

`run` remains active until `Ctrl+C`. Management commands are short-lived and exit after completing one operation.

**Why it exists**

This keeps terminal concerns separate from alarm and scheduling logic while avoiding separate notification and interaction abstractions that are unnecessary for this small CLI. Core behavior can still be tested through service-level inputs and outputs.

### Alarm Model and State Rules

**Responsibilities**

- Represent an alarm with a persistent numeric ID, a full local date-time, and a state.
- Support the states `Pending`, `Ringing`, and `Completed`.
- Enforce the valid transitions:
  - `Pending -> Ringing` when the trigger time is reached.
  - `Ringing -> Completed` when stopped.
  - `Ringing -> Pending` when snoozed, with the trigger time moved five minutes forward.

**Why it exists**

This centralizes lifecycle rules so the scheduler, persistence layer, and tests use the same behavior.

Although users enter only `HH:MM`, the model stores a full local date-time. This distinguishes today from tomorrow and preserves snooze times across restarts.

### Alarm Repository

**Responsibilities**

- Load and save alarms in `data/alarms.json`.
- Retrieve all alarms.
- Add, update, and delete alarms.
- Report a clear error for malformed JSON without overwriting the file.

**Why it exists**

This isolates JSON and filesystem behavior from the rest of the application. Persistence can be tested independently from scheduling.

All three states are persisted. Completed alarms remain stored unless a later requirement explicitly says they should be removed.

### Clock

**Responsibilities**

- Provide the current local system time.

**Why it exists**

Time is the main source of flaky tests. The scheduler and application services use a clock abstraction instead of calling the system clock directly. Tests can use a fixed or manually advancing clock without waiting in real time.

The application service owns conversion of an `HH:MM` value into the next local occurrence: today if the time has not passed, or tomorrow if it has passed.

### Scheduler

**Responsibilities**

- Load persisted alarms when `run` starts.
- Recover their states.
- Find pending alarms whose trigger time is due.
- Mark due alarms as `Ringing`.
- Process due alarms sequentially, ordered by trigger time and then ID.
- Coordinate with the CLI to notify the user and receive `stop` or `snooze` input for each ringing alarm.
- Persist every state change.

**Why it exists**

This owns all time-dependent behavior and restart recovery. It does not parse command-line arguments or know JSON details.

The scheduler should use a short polling loop. This is simpler and more realistic for the time limit than adding threads or a scheduling library.

## Restart Recovery

On scheduler startup:

- Future `Pending` alarms remain scheduled.
- Due `Pending` alarms become `Ringing` immediately.
- Persisted `Ringing` alarms are presented as ringing after restart so an alarm awaiting user action is not lost.
- `Completed` alarms are ignored by the scheduler.
- A recovered alarm remains one occurrence: stopping completes it; snoozing schedules its next five-minute occurrence.

## Main Flows

- **Set:** parse `HH:MM` -> calculate the next occurrence -> create a `Pending` alarm -> save.
- **List:** load alarms -> display all persisted alarms, including completed alarms.
- **Delete:** parse the numeric ID -> remove the alarm -> save.
- **Run:** load alarms -> recover due states -> poll the clock -> process due alarms sequentially.
- **Stop:** change `Ringing` to `Completed` -> save.
- **Snooze:** change `Ringing` to `Pending` five minutes later -> save.

## Test Scope

The focused test set should cover:

1. `HH:MM` resolves to today or tomorrow correctly.
2. Stopping changes `Ringing` to `Completed`.
3. Snoozing changes `Ringing` to `Pending` five minutes later.
4. Multiple due alarms are ordered by trigger time and then ID.
5. Future pending alarms survive save and load.
6. Due pending and ringing alarms recover correctly after restart.
7. Corrupt JSON produces a clear error without being overwritten.
8. CLI parsing maps commands to the correct operation.

## Composition

A small application entry point constructs the repository, clock, scheduler, and CLI dispatcher. Components receive these dependencies rather than constructing them internally, keeping the production setup simple and allowing tests to substitute a fixed clock or controlled inputs.

The design intentionally avoids threads, a database, external scheduling libraries, recurring alarms, and complex abstractions so it remains achievable within 30-45 minutes.
