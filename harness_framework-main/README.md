# Codex Harness Framework

Turn Claude-centered workflows like gStack and Superpower into a Codex-native framework.
This repo keeps the strong parts of the original workflow and rewrites them for Codex skills, Codex execution, and GitHub-friendly reuse.
It is inspired by gStack and Superpower style Claude workflows, but the current implementation is built for Codex.

## What This Repo Does

- Moves old Claude slash-command workflows into Codex skills.
- Uses `AGENTS.md` as the main project rule file.
- Runs implementation steps through `codex exec` with `scripts/execute.py`.
- Supports discovery, architecture planning, step planning, review, and optional git worktrees.
- Includes a safe starter template for `phases/` so new users can learn the structure quickly.

## Who This Is For

- People who used Claude workflows like gStack or Superpower and want the same ideas in Codex.
- Teams who want a repeatable TDD-first step runner for product work.
- People who want a study case for Codex skills, `agents/openai.yaml`, and workflow design.

## Core Layout

- `AGENTS.md`: project rules, hard guardrails, and development process.
- `docs/`: PRD, architecture, ADR, UI guide, and legacy Claude reference.
- `skills/`: Codex skills for each Harness stage.
- `scripts/execute.py`: Codex phase runner.
- `scripts/prompts/`: implementer and reviewer prompts.
- `templates/phases-starter/`: safe example files for learning and copy-starting a new project.
- `scripts/install_codex_skills.py`: installer for local Codex skills.
- `.github/workflows/ci.yml`: basic GitHub Actions test workflow.
- `SECURITY.md`: public repo security guidance.

## Install The Skills

Install the repo skills into Codex:

```bash
python3 scripts/install_codex_skills.py --mode symlink
```

Copy install:

```bash
python3 scripts/install_codex_skills.py --mode copy
```

List install targets:

```bash
python3 scripts/install_codex_skills.py --list
```

Installed skills:

- `harness-workflow`
- `harness-office-hours`
- `harness-brainstorm`
- `harness-step-planner`
- `harness-review`
- `harness-setup-worktrees`

Each skill includes `agents/openai.yaml`.
That file improves how the skill appears in Codex lists and gives a default prompt example.

## Suggested Flow

1. Write your project rules in `AGENTS.md`.
2. Fill `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md`, and `docs/UI_GUIDE.md`.
3. Use `harness-office-hours` or `harness-brainstorm` when you need help shaping the docs.
4. Use `harness-step-planner` to create `phases/index.json` and `phases/<phase>/step*.md`.
5. Run a phase:

```bash
python3 scripts/execute.py <phase-dir>
```

## Why It Is Different From The Old Claude Version

- `CLAUDE.md` is gone. `AGENTS.md` is the rule source now.
- Old `.claude` commands were rewritten as Codex skills.
- Execution now uses `codex exec`.
- Skill UI metadata is included through `agents/openai.yaml`.
- The legacy Claude workflow is preserved in `docs/LEGACY_CLAUDE_REFERENCE.md`.

## Safe Starter Template

If you want to learn the `phases/` format or start a new repo faster, use:

- `templates/phases-starter/README.md`

This template is safe because it lives under `templates/`, not the project root `phases/`.
`scripts/execute.py` will not run it unless you copy it into a real project.

Included example files:

- `templates/phases-starter/phases/index.json`
- `templates/phases-starter/phases/0-setup/index.json`
- `templates/phases-starter/phases/0-setup/step0.md`
- `templates/phases-starter/phases/0-setup/step1.md`

## Runner Features

- Injects `AGENTS.md` absolute guardrails into every step.
- Chooses default models and review levels by `complexity`.
- Carries recent completed-step summaries forward.
- Supports `none`, `spec-only`, and `full` review modes.
- Works without git for local experimentation.
- Uses branch, commit, and push flows when git exists.

## Step Frontmatter Example

```md
---
complexity: medium
review: full
principle: [ADR.md#철학]
context: [PRD.md#핵심 기능, ARCHITECTURE.md#디렉토리 구조]
---
```

## Publish Notes

If you publish this on GitHub, people can:

- install the Codex skills locally,
- study the `agents/openai.yaml` metadata pattern,
- copy the starter `phases/` template,
- and adapt older Claude workflow ideas to Codex.

## Public Repo Safety

- `.gitignore` blocks `.env`, Python cache files, local outputs, and worktree folders.
- `.env.example` shows how to document variables without publishing secrets.
- `SECURITY.md` explains what to review before publishing a fork or derived project.
- GitHub Actions runs the framework tests on push and pull request.

## Notes

- `--no-review`: skip review agents.
- `--push`: push after a phase completes.
- `--push` needs a git repo.
- Use `harness-setup-worktrees` for parallel phase work.
- Use `harness-review` for doc-aware code review.
