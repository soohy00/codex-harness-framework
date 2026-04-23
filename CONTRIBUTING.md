# Contributing

[English](./CONTRIBUTING.md) | [한국어](./CONTRIBUTING.ko.md)

Thanks for contributing to Codex Harness Framework.

## Before You Start

- Read `README.md` to understand the project goals.
- Read `AGENTS.md` to understand the workflow rules.
- Check `SECURITY.md` before sharing logs, examples, or configuration.

## Good First Contributions

- Improve skill instructions in `skills/`
- Improve starter examples in `templates/phases-starter/`
- Improve docs in `docs/`
- Improve test coverage in `scripts/test_*.py`
- Improve GitHub presentation and public onboarding

## Contribution Rules

- Keep the project Codex-first.
- Do not reintroduce `.claude`-specific runtime behavior.
- Keep examples safe for public reuse.
- Do not commit secrets, tokens, private keys, or real `.env` files.
- Use relative links in docs when linking to repo files.

## Workflow

1. Open an issue or start from an existing issue when the change is large.
2. Keep changes small and focused.
3. Update docs when behavior changes.
4. Add or update tests when needed.
5. Open a pull request with a clear summary.

## Local Checks

Run the full test suite before opening a pull request:

```bash
python3 -m unittest scripts.test_execute scripts.test_install_codex_skills scripts.test_skill_metadata scripts.test_phase_template scripts.test_repo_hygiene -v
```

Run syntax checks:

```bash
PYTHONPYCACHEPREFIX=/tmp/codex-pycache python3 -m py_compile scripts/execute.py scripts/test_execute.py scripts/install_codex_skills.py scripts/test_install_codex_skills.py scripts/test_skill_metadata.py scripts/test_phase_template.py scripts/test_repo_hygiene.py
```

## Pull Request Checklist

- The change is scoped and understandable
- Docs are updated if needed
- Tests pass locally
- No secrets or local artifacts are included
- `.gitignore` still protects local-only files

## License

By contributing to this repository, you agree that your contributions will be licensed under the MIT License in `LICENSE`.
