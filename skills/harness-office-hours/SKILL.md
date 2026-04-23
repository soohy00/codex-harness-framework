---
name: harness-office-hours
description: Use when the user wants YC-style discovery, asks to validate a startup or side-project idea, mentions /office-hours, or needs docs/DISCOVERY.md filled before design work. Supports startup mode and builder mode, asks one question at a time, and focuses on evidence over guesswork.
---

# Harness Office Hours

Validate the idea before design or implementation.

## Read First

1. `docs/DISCOVERY.md`
2. `docs/PRD.md`
3. `AGENTS.md`
4. Existing code if the repo already has implementation

## Working Rules

- Ask one question at a time.
- Prefer short choice-style questions when that helps.
- Treat evidence as stronger than opinions.
- Do not start architecture or code work in this stage.

## Mode Selection

- `startup` mode: new product, demand validation, market risk.
- `builder` mode: side project, internal tool, technical experiment.

If the user already hints at one mode, use it. If not, infer it from the repo and request.

## Startup Mode Flow

Ask these in order, one by one:

1. Who is already spending money or real effort on this problem?
2. How do they solve it today?
3. Who is the most concrete real user?
4. What is the smallest thing we can deliver this week?
5. What surprised the user during observation or conversation?
6. Does this get more needed or less needed over the next 3 years?

## Builder Mode Flow

1. Ask what they want to make and where they feel stuck.
2. Clarify goal, constraints, and success signal.
3. Offer 2 or 3 approaches with tradeoffs.
4. Help them choose one direction.

## Output

When the user is aligned, fill `docs/DISCOVERY.md` with:

- Problem definition
- Evidence of demand
- Current alternatives
- MVP hypothesis
- Validation criteria
- What is out of scope
- Observed thinking patterns

## Finish

- Summarize what is decided.
- Summarize what is still open.
- Suggest the next stage: `harness-brainstorm`.
