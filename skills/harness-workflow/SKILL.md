---
name: harness-workflow
description: Use when the user wants to run the Harness workflow in Codex, asks which stage to use next, or refers to the old Claude slash commands like /office-hours, /brainstorm, /harness, /review, or /setup-worktrees. Routes the request to the right local Harness skill and keeps the sequence office-hours -> brainstorm -> harness-step-planner -> execute/review/setup-worktrees.
---

# Harness Workflow

Use this skill when the user asks for the overall Harness flow or uses the old Claude command names.

## Stage Map

- Idea validation or problem discovery: use `skills/harness-office-hours/SKILL.md`.
- Technical design or architecture decisions: use `skills/harness-brainstorm/SKILL.md`.
- Step planning and `phases/` generation: use `skills/harness-step-planner/SKILL.md`.
- Code review against project docs: use `skills/harness-review/SKILL.md`.
- Parallel phase execution with git worktrees: use `skills/harness-setup-worktrees/SKILL.md`.

## Routing Rules

1. If the user mentions `/office-hours`, "startup mode", or "builder mode", use the office-hours skill.
2. If the user wants to turn product requirements into architecture and ADRs, use the brainstorm skill.
3. If the user wants to create or update `phases/index.json`, `phases/<phase>/index.json`, or `step*.md`, use the step planner skill.
4. If the user asks for review, use the review skill and present findings first.
5. If the user wants parallel execution by phase, use the setup-worktrees skill.

## Sequencing

- Do not jump into implementation during office-hours or brainstorm.
- Do not create `phases/` files before the user approves the proposed steps.
- After brainstorm is approved, suggest the step planner.
- After step planning is approved, suggest `python3 scripts/execute.py <phase-dir>`.

## Codex Notes

- This repo uses `AGENTS.md` as the main project rule file.
- `scripts/execute.py` already runs Codex, not Claude.
- Git is optional for local execution, but worktrees and push require a git repo.
