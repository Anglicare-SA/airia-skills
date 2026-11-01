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
| [`rtf-document`](skills/rtf-document/SKILL.md) | Writing a valid Rich Text Format (.rtf) document |

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

## Using these skills in a normal Airia agent

The gateway above serves skills to external MCP clients. A normal Airia agent can also use
them, without MCP, by loading them from this repository at run time:

1. **Python step** before the AI step. It lists `skills/` with the GitHub contents API,
   downloads each `SKILL.md` from `raw.githubusercontent.com` (no token, because the
   repository is public), and builds one text block: a catalog of names and descriptions,
   the full skill bodies, then the user's request. Load at most 20 skills.
2. **AI step** with no tools attached. Its prompt tells it to pick the skill that matches
   the request, follow it, and finish with `Skill used: <name>`.

To check it works, ask the agent to "run the skills gateway check". It should answer
`Gateway skills OK` and list every skill in this repository.

Things to know:

- The repository is public, so **never put credentials, personal information or
  internal-only detail in a skill**.
- GitHub limits unauthenticated API calls to 60 an hour per IP address. If the listing
  fails, the output begins `Problems: Could not list skills`. Heavy use may need a fixed
  skill list or a cached copy.
- Every skill is added to every run, so prompt size grows with the library.
- AI-step custom HTTP tools don't fill URL path placeholders, which is why the loader is a
  Python step rather than a tool.

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
