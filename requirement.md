Task: Build an alarm clock as a Python CLI application. CLI only, no web UI, no React, no database. There's no detailed spec; decide what to build with the time you have.


## Goal

Build a simple command-line alarm clock that allows to set and manage alarms and notifies the user when an alarm time is reached.

## Initial requirement 

- user should be able to set an alarm for a specific time.
- user should be able to view all the active alarms.
- user should be able to delete an alarm
- application should notify the user when an alarm is triggered.
- user should be able to snooze or stop the triggered alarm.
- Alarms should persist when the application is restarted

## Constraints

- python cli only.
- no web ui.
- no database
- keep implementation simple enought to build and validate within 30 minutes.

## Decision after review

Is an alarm one-time or recurring? - one time alarms (for now).
What does “specific time” mean: HH:MM, full date/time, or both? - HH:MM local time.
Which timezone applies? - local system timezone.
What should happen when setting an alarm for a time already passed? - next occurance tomm.
How are alarms identified for deletion? - pesistent numeric ID
What does “active” mean after an alarm rings? - completed 
What is the snooze duration, and can snooze be repeated? - 5 min and yes repeated allowrd
How should multiple alarms triggering close together behave? - handle sequentially
What notification is acceptable in a terminal: printed text, sound, or both? - terminal text and optional bell if allowed by terminal 
Where may persistence be stored, and what happens if the file is corrupt? - local json file 
What is the intended 30-minute scope? The current requirements could easily exceed it. - core lifecyle + persistence + tests 