---
name: airia-tagging-standard
description: Anglicare SA's fixed tag vocabulary for Airia agents. Use whenever you create, describe, review or retag an Airia agent, or when asked which tags an agent should have, so the Agents page filters stay clean.
license: Proprietary. Internal use at Anglicare SA only.
metadata:
  owner: sherennanayakkara
  version: "1.0"
---

# Airia tagging standard

Every Airia agent gets tags from this fixed vocabulary, in this order. Tags become filter
tabs on the Airia Agents page and are case-sensitive, so use the exact spelling below.

## 1. Sector: exactly one

Who uses the agent.

| Group | Tags |
|---|---|
| Service sectors | `Aged Care`, `Disability`, `Children & Families`, `Housing`, `Community Services` |
| Corporate | `Finance`, `P&C`, `T&I` |
| Everyone | `All Staff` (staff self-service and general tools) |

Add a new sector only for a whole division, never for a team.

## 2. System: zero to three

The product the agent works with. Name the product, not the action.

`AlayaCare`, `My Aged Care`, `TechOne`, `Freshservice`, `SharePoint`, `Microsoft 365`, `Snowflake`, `Airia`

Write `AlayaCare`, not `Client Creation`.

## 3. Type: exactly one

| Tag | Use for |
|---|---|
| `Assistant` | Open, general-purpose chat |
| `Knowledge Base` | Answers from a data store |
| `Automation` | Does work in another system |
| `Intake` | Structured interview or form |
| `Developer Tool` | Tools for builders |

## Rules

- Plain words, no prefixes, exact spelling.
- No one-off or descriptive tags such as `Ideas`, `GST`, `Receipts`, `Accreditation` or `IT Support`. They create clutter tabs.
- Retired tags: `HR` is now `P&C`, and `IT` is now `T&I`. Replace them when you touch an agent.

## Examples

| Agent | Tags |
|---|---|
| Freshservice IT Help Assistant | `All Staff`, `Freshservice`, `Knowledge Base` |
| An agent that creates clients in AlayaCare from referral PDFs | `Aged Care`, `AlayaCare`, `Automation` |
| A general chat assistant for the finance team | `Finance`, `Assistant` |

## How to answer

When asked to tag an agent, reply with the tags in order (sector, systems, type) and one
short line per tag explaining the choice. If a tag outside this vocabulary seems needed, say
so and suggest the closest allowed tag instead of inventing one.
