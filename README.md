# Airia Skills

Agent Skills for Anglicare SA, served through the Airia MCP Gateway (Skills over MCP) to
connected MCP clients such as Claude Code and goose.

A skill is a folder with a `SKILL.md`: frontmatter with a `name` and a description of when
to use it, then the instructions. Clients see only names and descriptions until a skill
matches the task, then read its instructions.

## Skills

| Skill | Use it for |
|---|---|
| [`airia-tagging-standard`](skills/airia-tagging-standard/SKILL.md) | Choosing and checking tags for Airia agents |
| [`skills-gateway-check`](skills/skills-gateway-check/SKILL.md) | Confirming gateway skills reach a client |

## How it's served

| Setting | Value |
|---|---|
| Gateway server type | Custom MCP server, transport **Skills Repository** |
| Repository | `https://github.com/Anglicare-SA/airia-skills` |
| Branch | `main` (protected; changes only arrive through reviewed pull requests) |
| Skills path | `skills` |
| Access | Fine-grained GitHub token with read-only **Contents** on this repository only, stored in the gateway's credential step |

Merged changes on `main` are picked up the next time the gateway fetches the repository.
To freeze what clients get, point the server at a tag instead of `main`.

## Rules the gateway applies (checked in CI)

The gateway skips a broken skill without any warning, so **Validate skills** fails the
pull request instead:

- The skill folder name must equal the frontmatter `name`: lowercase words joined by hyphens.
- Frontmatter may only use `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`.
- `SKILL.md` must be 256 KB or less, and a source can hold at most 20 skills. The gateway scans only the first 20.
- Every `SKILL.md` must sit under `skills/`. Category subfolders are fine.

CI also blocks credentials and common prompt-injection phrasing. The gateway's own scan
only reports risks and doesn't stop a skill being served, so review is the real control.

## Adding or changing a skill

1. Branch, then add `skills/<name>/SKILL.md` (and any reference files it links to).
2. Open a pull request. **Validate skills** and **Secret scan** must pass, and a code owner must approve.
3. Squash-merge. Clients get the change on the next fetch.
4. In Airia, open the gateway's **Select Skills** tab and switch the new skill on.

```bash
python -m pip install --require-hashes --no-deps -r .github/requirements-ci.txt
python -m pytest -q tests
python .github/scripts/validate_skills.py
```
