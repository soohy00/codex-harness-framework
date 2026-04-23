---
name: harness-review
description: Use when the user asks to review work done with the Harness framework, mentions /review, or wants changes checked against AGENTS.md, docs/ARCHITECTURE.md, docs/ADR.md, docs/PRD.md, and docs/UI_GUIDE.md. This skill prioritizes findings, checks architecture and quality, and can use codex review when useful.
---

# Harness Review

Review code against the project docs and Harness rules.

## Read First

1. `AGENTS.md`
2. `docs/ARCHITECTURE.md`
3. `docs/ADR.md`
4. `docs/PRD.md`
5. `docs/UI_GUIDE.md` if UI is involved

## Review Focus

Prioritize:

- Regressions
- Spec mismatches
- Missing tests
- Security and data integrity risk
- Architecture drift

## Process

1. Identify the change set.
2. Review the diff or changed files.
3. Compare the result against project docs.
4. Report findings first, ordered by severity.

When helpful, use:

```bash
codex review --uncommitted
```

or compare against a base branch with:

```bash
codex review --base main
```

## Checklist

- Follows `AGENTS.md` guardrails
- Matches `docs/ARCHITECTURE.md`
- Respects ADR decisions
- Supports PRD requirements
- Includes tests for new behavior
- Avoids banned UI patterns from `docs/UI_GUIDE.md`

## Output

- Findings first
- Then open questions or assumptions
- Then a short summary only if needed

If no findings remain, say that clearly and mention any residual test gap.
