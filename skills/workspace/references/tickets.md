# Ticket mechanics

Every command for one ticket, in workflow order. The policy lives in
`SKILL.md`. Read this file before you run the first ticket command in a
session.

## Rules for every command

- Add `rc.confirmation=off` to each `task` command that changes data. Without
  it, Taskwarrior can stop and wait for an answer that you cannot give.
- Add `rc.verbose=nothing` to each `task` command that reads data.
- Refer to a task by its UUID, or by the first 8 characters of the UUID.
- Do not use the short numeric IDs across steps. Taskwarrior renumbers them
  when a task is done.
- Do not create a task with `task add` or `task annotate`. Use `tw-new.py`.

## Find the project name

The workspace AGENTS.md declares the project name in a `Project:` line.
Read it there first.

When the workspace has no AGENTS.md, or the file gives no project name, use
the name of the directory:

```bash
basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
```

A subproject adds a dot and a name, for example `notes.auth`. In the
commands below, `<p>` is the project name.

## Create a ticket

1. Load the `simple-english` skill. Write every bullet with its rules.
2. Read the ticket schema:
   ```bash
   ~/.pi/agent/skills/workspace/scripts/tw-new.py --schema
   ```
3. Write the ticket as JSON. Start from the template in
   `assets/ticket-template.json` and replace each value. Never send the
   template to `tw-new.py` unchanged. Each bullet is one line of 3 to 200
   characters.
4. Send the JSON to `tw-new.py` on stdin:
   ```bash
   ~/.pi/agent/skills/workspace/scripts/tw-new.py <<'EOF'
   {
     "title": "Add text search to notes",
     "project": "notes.search",
     "tags": ["feature"],
     "depends": [],
     "problem": ["Notes cannot be found by their text"],
     "decision": ["Search the note files with ripgrep"],
     "artifacts": ["A search module in the notes package"],
     "risks": [
       {"risk": "Search is slow on a large repository",
        "detection": "One search takes more than 2 seconds"}
     ],
     "done_when": ["A search shows each match with its line number"]
   }
   EOF
   ```
5. If `tw-new.py` exits with 0, it prints the UUID of the new task. Keep this
   UUID.
6. If `tw-new.py` exits with 1, it prints one line for each error. Each line
   gives the field and the rule. Correct the JSON and send it again.
   `tw-new.py` creates no task when it finds an error.

`depends` holds the UUIDs of tasks that must be done first. `tw-new.py` stops if a
UUID does not match a task.

## Start and finish work

- To start a task: `task rc.confirmation=off <uuid> start`
- To finish a task: `task rc.confirmation=off <uuid> done`

## Replace a ticket

- Create the new ticket with `tw-new.py`. Write the new decision and its
  reasons. Follow "Create a ticket" above.
- Close the old ticket as canceled:
  `task rc.confirmation=off <old-uuid> delete`

Use `delete`, not `done`. The old ticket was not finished.

## Show the state of work

Each command prints one line for each task: the UUID prefix, the status, and
the title.

```bash
Q='.[] | "\(.uuid[0:8])  \(.status)  \(.description | split("\n")[0])"'
task rc.verbose=nothing project:<p> +ACTIVE export | jq -r "$Q"     # started
task rc.verbose=nothing project:<p> +READY export | jq -r "$Q"      # can start now
task rc.verbose=nothing project:<p> +BLOCKED export | jq -r "$Q"    # waits on other tasks
task rc.verbose=nothing project:<p> status:completed end.after:today-7d export | jq -r "$Q"
task rc.verbose=nothing project:<p> status:pending count
```

To give a summary, use these groups in this order: started, ready, blocked,
done in the last 7 days. Write the summary with the `simple-english` rules.

## Show how a ticket relates to other tickets

- `+BLOCKED` tasks wait on other tasks. `+BLOCKING` tasks stop other tasks.
- To list each dependency in a project as an edge, run this command:
  ```bash
  task rc.verbose=nothing project:<p> export \
    | jq -r '.[] | select(.depends) | .uuid[0:8] as $u | .depends[] | "\($u) --> \(.[0:8])"'
  ```
  Each line shows that the first task waits on the second task.
- To show the relations to the user, read
  `~/.pi/agent/skills/show-me/SKILL.md` and follow it.

## Close out a ticket

Run the close script with the ticket UUID and, when the document is not at
the default path, the document path:

```bash
~/.pi/agent/skills/workspace/scripts/tw-close.py <uuid> [document]
```

The default document is `conclusions/<ticket-id>.md`. The script makes sure
that the ticket is open and that the document is complete. Then it
annotates the ticket with the path and prints the next steps for the user.
