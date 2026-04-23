---
name: harness-setup-worktrees
description: Use when the user wants to run Harness phases in parallel, mentions /setup-worktrees, or asks to create git worktrees per phase. This skill validates repo state, chooses a worktree root, creates one worktree per phase, installs dependencies when needed, and explains how to run scripts/execute.py in each worktree.
---

# Harness Setup Worktrees

Create one git worktree per phase for parallel execution.

## Preconditions

- A git repo must exist.
- `phases/index.json` must exist.
- Each target phase must already have its own `index.json`.

## Workflow

### 1. Check Readiness

Confirm:

- git repo root
- clean enough working tree
- `phases/index.json` contents

If there are uncommitted changes that make worktrees risky, stop and tell the user.

### 2. Choose the Worktree Root

Use this order:

1. Existing `.worktrees/`
2. A user-provided path
3. Ask the user to choose between repo-local `.worktrees/` and an external path

### 3. Create Worktrees

For each phase:

```bash
git worktree add {path}/{phase_dir} -b feat-{phase_name}
```

If the branch already exists, attach to it instead of failing.

### 4. Install Dependencies

Install only what the repo actually uses:

- `npm install`
- `pip install -r requirements.txt`
- `cargo build`

### 5. Smoke Test

Run the smallest useful test command for each worktree and report the result.

## Finish

Show, for each phase:

- path
- branch
- command to run

Use this execution format:

```bash
cd {worktree_path}/{phase_dir}
python3 scripts/execute.py {phase_dir}
```
