# Job Layout

This document describes what a job directory holds and what each state means.
It is a reference. The procedure is in `SKILL.md`.

## Directory

Each job gets one directory. The default root is `~/.pi/jobs/`. The
environment variable `PI_JOBS_DIR` sets a different root for one call.

```
~/.pi/jobs/
├── .gitignore              # holds a single "*", so the directory excludes itself
└── pytest-20260823-181500-4417/
    ├── cmd                 # the command, quoted for a shell, on one line
    ├── cwd                 # the directory the job started in
    ├── started_at          # start time, ISO 8601, UTC
    ├── pid                 # process group id of the job
    ├── stdout.log          # standard output, exactly as the command wrote it
    ├── stderr.log          # standard error, exactly as the command wrote it
    ├── stopped             # time of a bg-stop request; absent unless bg-stop ran
    └── exit                # exit code; this file exists only when the job is complete
```

The job id has three parts: a name, a UTC timestamp, and the process id of the
script that started the job. The timestamp makes the ids sort in start order.

## One fact per file

Every metadata file holds one value and needs no parser. A reader gets any
value with `cat`. No file holds JSON, so no value needs an escape rule.

## The exit file is the completion signal

The `exit` file exists only after the command finishes. The wrapper writes the
code to `exit.tmp` and then renames that file to `exit`. A rename is atomic on
a local filesystem, so a reader never sees a half-written code.

This design removes the usual race. A reader does not compare timestamps or
watch a process. The presence of one file answers the question.

## States

| State | Meaning |
|---|---|
| `starting` | The directory exists. The wrapper has not written `pid` yet. This state lasts under a second. |
| `running` | The `pid` is alive and no `exit` file exists. |
| `exited` | The `exit` file exists. Its content is the exit code of the command. |
| `stopping` | A `stopped` file exists and the process is still alive. The job is inside the grace period of `bg-stop`. |
| `stopped` | A `stopped` file exists, the process is gone, and no `exit` file exists. A person or an agent stopped this job. |
| `vanished` | No `exit` file, no `stopped` file, and the `pid` is gone. The job was killed with `-9`, or the machine restarted. |

The `vanished` state is the reason `bg-status` reads both the exit file and the
process. A check of the process alone reports a dead job as running forever.

The `stopped` state exists because a TERM signal usually reaches the wrapper
before the wrapper can record an exit code. Without the marker, every deliberate
stop looks the same as an unexplained loss.

## Separate logs

Standard output and standard error go to different files. A count of the lines
in `stderr.log` answers the question "did this job complain?" without a search
through the output.

The cost of this design is order. The two files have no shared timeline, so the
exact interleaving of the two streams is lost. A job whose diagnosis depends on
that order needs `2>&1` inside its own command.

## Raw logs

The logs hold the bytes of the command, with no added timestamp and no added
prefix. A log is therefore identical to the terminal output of the same
command. Times live in `started_at` and in the modification time of `exit`.

## Process group

The wrapper runs under `setsid`, so the job is a process group leader. The
`pid` file holds that group id. A signal to the negative group id reaches the
command and every child of the command.

A command that starts its own daemon is the exception. A daemon that leaves the
group survives `bg-stop`.

A signal to the group also reaches the wrapper. A command with its own TERM
handler therefore cannot record an exit code through `bg-stop`, because the
wrapper stops at the same moment. The `stopped` state is the record instead.
This is a deliberate trade: one process group is what makes every child of the
command stop as well.

## Stdin

The job reads from `/dev/null`. A command that waits for input gets an
end-of-file and stops. This is deliberate: a background job that blocks on a
prompt is invisible, because no terminal shows the prompt.
