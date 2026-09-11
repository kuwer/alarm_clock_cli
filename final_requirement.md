

1. **Application lifecycle remains undecided.**  
   The requirements cannot be implemented or tested until it is clear whether the CLI stays running and waits for alarms. A command that exits after setting an alarm cannot notify the user when the time is reached.

   - `alarm run` is a long-runnig scheduler and exits with `cntrl + c`
   - managements commands (set, list, delete) are short lived commands

2. **“One-time” conflicts with `HH:MM` plus “tomorrow.”**  
   An `HH:MM` alarm has no date. Treating a past time as tomorrow makes it a scheduled occurrence, but the behavior after restart or after a missed alarm is still undefined.

   - alarm are one-time and fiere only once.
   - `HH:MM` represent the next occurance in the local system timezone.
   - A past time is scheduled for the following day.



3. **“Completed” conflicts with repeated snoozing.**  
   If a triggered alarm becomes completed, it is unclear whether snoozing changes it back into an active alarm. Without that state transition, repeated snooze cannot be implemented or tested consistently.

   - Stopping a ringing alarm marks it `Completed`.
   - Snoozing moves the same alarm back to `Pending` for 5 minutes later and can be repeated.

4. **Sequential handling of simultaneous alarms is underspecified.**  
   “Sequentially” does not define ordering or whether the application waits for the user to stop/snooze one alarm before presenting the next. This affects observable behavior and tests.

   - multiple due alarams are processed sequentually , ordered by triggerd time and then ID.

5. **The persistence requirement is incomplete.**  
   “Local JSON file” does not specify its location or what state must be persisted: scheduled alarms only, completed alarms, or snoozed alarms. This is especially important across restart tests.

   - Alarms are persisted in `data/alarms.json`.
   - pending, ringing and compelted states are persisted.
   - a corrupted persistent file results in a clear error rather than being overwritten.

6. **The 30-minute scope is still too broad to validate reliably.**  
   “Core lifecycle + persistence + tests” does not define which workflows must be covered, while the requirements include waiting, triggering, stopping, repeated snoozing, deletion, restart behavior, and multiple alarms.
   
    - The MVP prioritize the compelte alarm lifecycle, persistence, recovert and core testes


