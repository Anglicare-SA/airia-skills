# Security

`SKILL.md` text is placed directly into an AI model's context, so a malicious or careless
skill has the same risk as a malicious tool description.

| Control | Where |
|---|---|
| Code owner review of every change; protected, signed, linear `main` | `.github/CODEOWNERS`, ruleset `Protect main` |
| Prompt-injection and credential checks on every skill and its files | `.github/scripts/validate_skills.py` |
| gitleaks scan of every pull request and push | `.github/workflows/ci.yml` |
| Dependabot alerts and security updates | repository settings |
| Read-only, single-repository token for the gateway | Airia gateway credential step |
| Airia Policy Engine scan of each `SKILL.md` (advisory only) | Airia Tool Scanning |

All controls use free GitHub features; the paid Secret Protection and Code Security add-ons are off.

Never put credentials, personal information or client data in a skill. If you find any,
tell the repository owner directly so it can be rotated and removed from history.
