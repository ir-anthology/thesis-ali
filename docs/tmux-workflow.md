# tmux Workflow — `thesis-ali`

A reproducible tmux workspace for this thesis project: one session, three windows,
nine panes, each pane in the right directory with a title in its border.

- **Script:** `~/bin/thesis-ali`
- **tmux config:** `~/.tmux.conf`
- **Project root:** `/home/dev/Documents/Work/Hiwi/thesis-ali`

---

## 1. Workspace structure

```
Session: thesis-ali
│
├── Window 1: backend
│   Directory: sparql/option-4-rule-based-sparql-generation
│   ├── agent
│   ├── terminal
│   └── file_explorer
│
├── Window 2: frontend
│   Directory: frontend/adaptive
│   ├── agent
│   ├── terminal
│   └── file_explorer
│
└── Window 3: deployment
    Directory: sparql/option-4-rule-based-sparql-generation
    ├── git
    ├── docker
    └── k8s
```

Every window uses the same layout: one large pane on the left, two smaller panes
stacked on the right (65% / 35% width, right column split 50/50).

```
┌────────────────────────┬──────────────┐
│                        │   terminal   │
│                        ├──────────────┤
│         agent          │ file_explorer│
│                        │              │
└────────────────────────┴──────────────┘
```

> **Window and pane numbering starts at 1**, because `~/.tmux.conf` sets
> `base-index 1` and `pane-base-index 1`. Press `prefix + 1/2/3`, not `0/1/2`.

Panes start as plain interactive shells. The script does **not** launch an AI
agent, a file explorer, Docker, or Kubernetes commands — those titles only mark
what each pane is meant for.

---

## 2. Prerequisites

```bash
sudo apt update
sudo apt install -y tmux
tmux -V          # 3.6
```

Optional but recommended, so yanking in copy mode writes to the real clipboard
(the config falls back to OSC 52 / `wl-copy` / `xclip`, in that order):

```bash
sudo apt install -y wl-clipboard
```

---

## 3. The startup script

`~/bin/thesis-ali`:

```bash
#!/usr/bin/env bash
# thesis-ali — repeatable tmux workspace for the thesis project.
# Usage: thesis-ali [-f|--fresh]   (-f rebuilds the session from scratch)
set -euo pipefail

SESSION="thesis-ali"
ROOT="${THESIS_ROOT:-/home/dev/Documents/Work/Hiwi/thesis-ali}"

BACKEND="$ROOT/sparql/option-4-rule-based-sparql-generation"
FRONTEND="$ROOT/frontend/adaptive"
DEPLOYMENT="$BACKEND"

FRESH=0
case "${1:-}" in
    -f|--fresh) FRESH=1 ;;
    -h|--help)
        cat <<EOF
Usage: thesis-ali [-f|--fresh]

  (no args)   attach to the "$SESSION" session, creating it if needed
  -f, --fresh kill any existing "$SESSION" session and rebuild it
EOF
        exit 0
        ;;
    "") ;;
    *)  echo "Unknown argument: $1 (try --help)" >&2; exit 2 ;;
esac

die() { echo "Error: $*" >&2; exit 1; }

# 1. Verify project directories.
for dir in "$BACKEND" "$FRONTEND" "$DEPLOYMENT"; do
    [[ -d "$dir" ]] || die "Directory not found: $dir"
done

# 2. Attach if the session already exists (unless --fresh).
if tmux has-session -t "=$SESSION" 2>/dev/null; then
    if (( FRESH )); then
        # Nested clients would be left dangling; warn but proceed.
        tmux kill-session -t "=$SESSION"
    else
        echo "Session '$SESSION' already exists — attaching."
        echo "  (run 'thesis-ali --fresh' to rebuild it)"
        exec tmux attach-session -t "=$SESSION"
    fi
fi

# 3. Create a window with three panes:
#      left = main task, right = terminal on top, file explorer below.
# Pane ids are captured so the script works with any base-index setting.
create_workspace_window() {
    local main="$1" directory="$2"
    local left_title="$3" top_title="$4" bottom_title="$5"

    tmux select-pane -t "$main" -T "$left_title"

    # Split left/right; 35% of the width goes to the right-hand column.
    local right
    right=$(tmux split-window -h -p 35 -t "$main" -c "$directory" -P -F '#{pane_id}')

    # Split the right column into two stacked panes.
    local bottom
    bottom=$(tmux split-window -v -p 50 -t "$right" -c "$directory" -P -F '#{pane_id}')

    tmux select-pane -t "$right"  -T "$top_title"
    tmux select-pane -t "$bottom" -T "$bottom_title"

    # Return focus to the main pane.
    tmux select-pane -t "$main"
}

# Window 1: backend
pane=$(tmux new-session -d -s "$SESSION" -n backend -c "$BACKEND" -P -F '#{pane_id}')
create_workspace_window "$pane" "$BACKEND" agent terminal file_explorer

# Window 2: frontend
pane=$(tmux new-window -d -t "$SESSION:" -n frontend -c "$FRONTEND" -P -F '#{pane_id}')
create_workspace_window "$pane" "$FRONTEND" agent terminal file_explorer

# Window 3: deployment
pane=$(tmux new-window -d -t "$SESSION:" -n deployment -c "$DEPLOYMENT" -P -F '#{pane_id}')
create_workspace_window "$pane" "$DEPLOYMENT" git docker k8s

# 4. Start on the backend window, with the main pane focused.
tmux select-window -t "$SESSION:backend"
tmux select-pane -t "$SESSION:backend.{top-left}"

exec tmux attach-session -t "$SESSION"
```

Install it:

```bash
mkdir -p ~/bin
chmod +x ~/bin/thesis-ali
```

The `--help` branch prints:

```
Usage: thesis-ali [-f|--fresh]

  (no args)   attach to the "thesis-ali" session, creating it if needed
  -f, --fresh kill any existing "thesis-ali" session and rebuild it
```

### `~/bin` on `PATH`

Added to `~/.bashrc` (idempotent, so it is never duplicated):

```bash
# personal scripts (~/bin)
case ":$PATH:" in
  ":$HOME/bin:"*) ;;
  *) export PATH="$HOME/bin:$PATH" ;;
esac
```

Only new shells pick this up — open a fresh terminal or `source ~/.bashrc`.

---

## 4. Start the workspace

```bash
thesis-ali            # create if missing, otherwise attach
thesis-ali --fresh    # kill the old session and rebuild it
thesis-ali --help
```

The script:

1. Verifies that the project directories exist.
2. Attaches to the existing session if one is already running.
3. Otherwise creates all three windows and their nine panes.
4. Sets each pane's working directory (via `-c`) and its title (via `-T`).
5. Focuses the left `agent` pane of the `backend` window and attaches.

Working root can be overridden without editing the script:

```bash
THESIS_ROOT=/some/other/checkout thesis-ali
```

---

## 5. Navigation

Prefix is **`C-b`** — or **`C-a`** if you prefer; both are bound, and
`C-b C-b` / `C-a C-a` sends a literal prefix through to the program.
The table below uses `prefix` for either.

| Shortcut | Action |
| --- | --- |
| `prefix`, `1` | backend window |
| `prefix`, `2` | frontend window |
| `prefix`, `3` | deployment window |
| `prefix`, `o` | next pane |
| `prefix`, arrow key | move between panes |
| `C-h` / `C-j` / `C-k` / `C-l` | move between panes without prefix (falls through to vim at the edge) |
| `prefix`, `H/J/K/L` | resize pane by 5 cells (repeatable) |
| `prefix`, `z` | zoom / restore current pane |
| `prefix`, `|` / `-` | split left-right / top-bottom, in the current directory |
| `prefix`, `c` | new window, in the current directory |
| `prefix`, `d` | detach from the session |
| `prefix`, `r` | reload `~/.tmux.conf` |
| `prefix`, `X` | kill the current pane (asks for confirmation) |

### Copy mode (vi keys)

`prefix`, `[` enters copy mode. `v` starts a selection, `V` selects a line,
`C-v` toggles block selection, `y` yanks and exits, `Esc` cancels. Mouse drag
also copies. Copies go to the system clipboard through `wl-copy` / `xclip` when
installed, otherwise via terminal OSC 52.

---

## 6. Managing the session

```bash
tmux ls                                     # list sessions
tmux a -t thesis-ali                        # reconnect
tmux list-windows -t thesis-ali             # windows
tmux list-panes -a -F \
  '#{window_name}.#{pane_index} | #{pane_title} | #{pane_current_path}'
```

Expected pane listing (paths shortened):

```
backend.1    | agent         | .../sparql/option-4-rule-based-sparql-generation
backend.2    | terminal      | .../sparql/option-4-rule-based-sparql-generation
backend.3    | file_explorer | .../sparql/option-4-rule-based-sparql-generation
frontend.1   | agent         | .../frontend/adaptive
frontend.2   | terminal      | .../frontend/adaptive
frontend.3   | file_explorer | .../frontend/adaptive
deployment.1 | git           | .../sparql/option-4-rule-based-sparql-generation
deployment.2 | docker        | .../sparql/option-4-rule-based-sparql-generation
deployment.3 | k8s           | .../sparql/option-4-rule-based-sparql-generation
```

Stop the workspace:

```bash
tmux kill-session -t thesis-ali
```

⚠ Killing the session terminates every process running inside it — dev servers,
the AI agent, test runs. It also sends you back to your shell if you are
attached. Recreating with `thesis-ali --fresh` does the same thing.

---

## 7. tmux configuration summary

`~/.tmux.conf`, relevant settings:

| Area | Setting |
| --- | --- |
| Terminal | `tmux-256color`, truecolor, `allow-passthrough on`, `escape-time 0` |
| Indices | `base-index 1`, `pane-base-index 1`, `renumber-windows on` |
| Prefix | `C-b` and `C-a` |
| Mouse | `mouse on`, scroll enters copy mode, drag copies |
| Clipboard | `set-clipboard on` + auto-detected `copy-command` |
| Splits | keep the current directory |
| History | 50 000 lines |
| Borders | `pane-border-status top`, titles in the border, heavy lines |
| Session | `detach-on-destroy off` (killing a session switches instead of exiting) |

---

## 8. Daily workflow

1. `thesis-ali` — reattach or rebuild the workspace.
2. **backend** window: SPARQL generation and API development.
3. **frontend** window: UI work and tests.
4. **deployment** window: Git, Docker and Kubernetes tasks.
5. `prefix`, `d` to detach when you leave the terminal; run `thesis-ali` later.
6. `thesis-ali --fresh` only when the layout itself changed.

---

## 9. Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `Error: Directory not found: …` | Project tree moved or `THESIS_ROOT` is wrong. |
| `Session 'thesis-ali' already exists — attaching.` | Expected. Use `--fresh` to rebuild. |
| Windows are numbered 0,1,2 | That server started before `~/.tmux.conf` existed. `tmux kill-server`, then `thesis-ali`. |
| Pane titles show the hostname (`asus`) | Same cause: the config with `pane-border-status` was not loaded. Restart the server. |
| `y` in copy mode does not reach the clipboard | `sudo apt install wl-clipboard`, then reload the config (`prefix`, `r`). |
| `thesis-ali: command not found` | New shell needed after the `~/.bashrc` change, or call `~/bin/thesis-ali`. |
| `sudo: interactive authentication is required` | Run the `apt` line yourself; sudo here needs a typed password. |
