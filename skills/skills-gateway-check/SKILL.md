---
name: skills-gateway-check
description: Confirms that skills from the Anglicare SA skills repository are reaching this client through the Airia MCP Gateway. Use when someone asks to test, check or verify that gateway skills work.
license: Proprietary. Internal use at Anglicare SA only.
metadata:
  owner: sherennanayakkara
  version: "1.0"
---

# Skills gateway check

If you are reading this, the skill was delivered by the Airia MCP Gateway from the
`Anglicare-SA/airia-skills` repository.

When asked to check gateway skills:

1. Reply with the exact line: `Gateway skills OK: skills-gateway-check v1.0`
2. List the names of the other skills you can see in the gateway's skill catalog.
3. Mention any skill you expected but can't see. The gateway skips a skill without warning
   when its folder name and `name` don't match, or when its frontmatter has fields outside
   `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`.
