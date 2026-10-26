# Security

`SKILL.md` text is placed directly into an AI model's context, so a malicious or careless
skill has the same risk as a malicious tool description.

| Control | Where |
|---|---|
| Code owner review of every change; protected, signed, linear `main` | `.github/CODEOWNERS`, ruleset `Protect main` |
| Prompt-injection and credential checks on every skill and its files | `.github/scripts/validate_skills.py` |
| gitleaks scan of every pull request and push | `.github/workflows/ci.yml` |
| Secret scanning with push protection; Dependabot | repository settings |
| Read-only, single-repository token for the gateway | Airia gateway credential step |
| Airia Policy Engine scan of each `SKILL.md` (advisory only) | Airia Tool Scanning |

Never put credentials, personal information or client data in a skill. If you find any,
tell the repository owner directly so it can be rotated and removed from history.
