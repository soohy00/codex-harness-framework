---
name: harness-step-planner
description: Use when the user wants to create or revise Harness implementation phases, generate phases/index.json or step markdown files, mentions /harness, or wants a Codex execution plan based on docs/PRD.md, docs/ADR.md, docs/ARCHITECTURE.md, and docs/UI_GUIDE.md. This skill plans small TDD-first steps, asks for approval before writing phase files, and aligns steps with scripts/execute.py.
---

# Harness Step Planner

Plan Codex execution steps from the approved docs.

## Read First

1. `docs/DISCOVERY.md`
2. `docs/PRD.md`
3. `docs/ADR.md`
4. `docs/ARCHITECTURE.md`
5. `docs/UI_GUIDE.md` if the product has UI
6. Existing code and tests

## Planning Rules

- Keep one step focused on one layer or module.
- Make each step self-contained.
- Put required file paths directly in the step file.
- Keep TDD order explicit.
- Use runnable commands for acceptance criteria.
- Explain bans with a reason.

## Complexity Mapping

Use these defaults unless the repo needs an override:

| complexity | use for | default model | default review |
|---|---|---|---|
| `low` | config, scaffold, simple CRUD, straightforward UI | `gpt-5.4-mini` | `none` |
| `medium` | business logic, API work, state handling | `gpt-5.4` | `spec-only` |
| `high` | auth, payments, core architecture, security-sensitive work | `gpt-5.2` | `full` |

## Recommended Flow

### 1. Draft the Phases

Propose the phase list first.

### 2. Draft the Steps

Within each phase, propose step names, complexity, and main outcome.

### 3. Ask for Approval

Do not write `phases/` files until the user approves the structure.

### 4. Generate Files

After approval, create:

- `phases/index.json`
- `phases/<phase>/index.json`
- `phases/<phase>/step<N>.md`

## Step File Requirements

Each `step<N>.md` should include:

- frontmatter with `complexity`
- `prescriptive` for `low` steps when needed
- `principle` for `medium` or `high`
- `context` for `medium` or `high`
- files to read first
- TDD-first task checklist
- acceptance criteria with runnable commands
- index update rules
- bans with reasons

## Compatibility Notes

- Refer to `AGENTS.md`, not `CLAUDE.md`.
- These steps are executed by `python3 scripts/execute.py <phase-dir>`.
- `scripts/execute.py` now calls Codex, so write instructions for Codex runs.
- If git is optional in the current clone, phrase commit steps as conditional.

## Finish

After generating files:

1. Check for leftover placeholders in `phases/**/*.md`.
2. Tell the user how to run the first phase.
3. Suggest `harness-setup-worktrees` only if they want parallel phase work.
