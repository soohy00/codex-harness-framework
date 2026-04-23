---
name: harness-brainstorm
description: Use when the user wants to turn validated product requirements into technical design, fill docs/ADR.md or docs/ARCHITECTURE.md or docs/UI_GUIDE.md, or mentions /brainstorm. This skill explores context, asks focused clarification questions, proposes 2 to 3 technical approaches, gets approval in sections, and writes the design docs without placeholders.
---

# Harness Brainstorm

Turn discovery into an approved technical design.

## Read First

1. `docs/DISCOVERY.md`
2. `docs/PRD.md`
3. `AGENTS.md`
4. `docs/ARCHITECTURE.md` if it already exists
5. Existing code if the repo already has implementation

## Guardrails

- Do not implement code in this stage.
- Remove placeholders instead of leaving `{...}` behind.
- Keep questions focused and ask one at a time when the answer matters.

## Flow

### 1. Context Check

- If `docs/PRD.md` still has placeholders, fill the business sections from `docs/DISCOVERY.md`.
- Ask the user to confirm the PRD if major assumptions remain.

### 2. Clarification

Clarify only the decisions that change architecture:

- External integrations
- Performance needs
- Deployment target
- Team size and maintenance
- Deadline or launch pressure

### 3. Approach Options

Present 2 or 3 approaches.

For each one include:

- Core choice
- Main benefits
- Main risks
- Best fit
- Recommendation

Default to the simplest option that can work.

### 4. Approval by Section

Get alignment in this order:

1. Tech stack
2. Directory structure
3. Data flow
4. External dependencies
5. UI design principles

### 5. Write Docs

After approval, update:

- `docs/ADR.md`
- `docs/ARCHITECTURE.md`
- `docs/UI_GUIDE.md`

Requirements:

- Use concrete values.
- Do not leave placeholders.
- Keep `docs/UI_GUIDE.md` anti-pattern table unchanged.

### 6. Self-Check

Before finishing, verify:

- No placeholders remain
- No vague wording remains
- ADR and architecture do not conflict
- Another step planner could work from these docs alone

## Finish

- Point the user to the updated docs.
- Ask for review.
- When approved, suggest the next stage: `harness-step-planner`.
