---
name: background-jobs
description: |
  Start a shell command in the background and track it through files. Use for a
  command that takes too long to wait for: a test suite, a build, a training
  run, a data load, or a long migration. Each job gets a directory under
  ~/.pi/jobs/ that holds the command, a separate stdout log, a separate stderr
  log, and an exit-code file that exists only when the job is complete. Use
  when the user says "run this in the background", "start a long job", "check
  on the job", "tail the log", or asks why a background command failed.
license: MIT
---

# Background Jobs

Start a command and get a job id. Read the result later from files. The command
continues after the tool call returns.

The scripts are in `~/.pi/agent/skills/background-jobs/scripts/`. Call them by
full path. Shell state does not survive between tool calls, so `PATH` and
aliases do not help.

## Where jobs live

The default root for the jobs is `~/.pi/jobs`. Every script finds the jobs
there, from any working directory.

To use a different root, set `PI_JOBS_DIR` at the start of the command:

```bash
PI_JOBS_DIR="$PWD/.pi/jobs" ~/.pi/agent/skills/background-jobs/scripts/bg-start -- pytest -q
```

Shell state does not survive between tool calls. Set the variable on each
call for as long as you use that root.

## Start a job

Put the command after `--`:

```bash
~/.pi/agent/skills/background-jobs/scripts/bg-start --name pytest -- pytest -q
```

The script prints the job id. Keep this id. Every other command needs it.

`--name` sets the first part of the job id. If you give no name, the script
uses the name of the command.

## Check the state

```bash
~/.pi/agent/skills/background-jobs/scripts/bg-status
~/.pi/agent/skills/background-jobs/scripts/bg-status <job-id>
```

The first form lists every job. The second form lists one job, and also prints
its command and its working directory.

Each row gives the state, the exit code, the elapsed seconds, and the size of
each log in bytes.

## Read the logs

```bash
~/.pi/agent/skills/background-jobs/scripts/bg-tail <job-id>
~/.pi/agent/skills/background-jobs/scripts/bg-tail --err <job-id>
~/.pi/agent/skills/background-jobs/scripts/bg-tail --lines 200 <job-id>
```

`bg-tail` prints the last 50 lines of `stdout.log`. `--err` reads `stderr.log`
instead.

Read `bg-status` first. If a log is large, the whole file does not fit in
context.

To search a log instead of reading it, use `grep` on the file directly:

```bash
grep -n 'Error' ~/.pi/jobs/<job-id>/stderr.log
```

## Stop a job

```bash
~/.pi/agent/skills/background-jobs/scripts/bg-stop <job-id>
```

The script signals the process group with TERM, waits 10 seconds, then sends
KILL. Use `--grace-seconds N` for a different wait.

## States

| State | Meaning | Next step |
|---|---|---|
| `starting` | The job has not registered yet. | Run `bg-status` again. |
| `running` | The job is alive. | Wait, or read the log so far. |
| `exited` | The job finished and recorded its code. | Read the exit code. |
| `stopping` | `bg-stop` sent TERM and the job is still alive. | Wait for the grace period to end. |
| `stopped` | `bg-stop` ended the job before it finished. | Read the logs for the work done so far. |
| `vanished` | The job is gone, and nobody stopped it. | Read both logs. The job was killed, or the machine restarted. |

## Rules

Report the exit code, not the log volume. A job with code `0` and an empty
`stderr.log` needs no further report.

If the exit code is not `0`, read `stderr.log` first. Read `stdout.log` only
when `stderr.log` gives no cause.

Do not poll in a loop. Start the job, do other work, then check the state once
the other work is complete.

Do not start a job that waits for input. The job reads from `/dev/null`, so a
prompt gets an end-of-file and the job stops.

If a job must record the exact order of output and errors, put `2>&1` inside
the command. The two logs have no shared timeline.

## Reference

`references/job-layout.md` describes the job directory, the file formats, and
the reason the `exit` file is the completion signal.
