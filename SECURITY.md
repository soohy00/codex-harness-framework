# Security

## Supported Use

This repository is a framework template for Codex workflows.
It is designed to be copied and adapted to real projects.

## Secret Handling

- Do not commit real `.env` files.
- Do not commit API keys, tokens, private keys, or customer data.
- Use `.env.example` only as a placeholder file.
- Keep project-specific secrets in local environment files or your secret manager.

## Safe Public Sharing

Before publishing your own fork or derived project:

1. Remove real credentials from code, logs, and examples.
2. Check `AGENTS.md`, `docs/`, and `phases/` for internal names or private paths.
3. Make sure generated outputs in `phases/**/step*-output.json` are not committed.
4. Review `.gitignore` to confirm local files and `.env` files stay private.

## Reporting

If you find a security problem in this framework, please avoid posting secrets in a public issue.
Open a private report through your preferred secure channel first.
