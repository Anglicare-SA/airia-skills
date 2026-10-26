"""Validate skills against the rules the Airia MCP Gateway applies.

The gateway silently skips a skill that breaks its rules, so this check fails loudly instead:
- every folder with a SKILL.md is a skill; its frontmatter `name` must equal the folder name
- frontmatter may only use: name, description, license, compatibility, metadata, allowed-tools
- SKILL.md over 256 KB is skipped by the gateway's scanner
- only the first 20 skills per source are scanned
It also checks for credentials and common prompt-injection phrasing, because SKILL.md text
goes straight into the model's context and the gateway's scan doesn't block.

Writes GitHub annotations and a Markdown summary ($GITHUB_STEP_SUMMARY). Exit 1 on errors.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME, MAX_DESCRIPTION = 64, 1024
MAX_BYTES = 256 * 1024
MAX_SCANNED = 20
SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("bearer token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/-]{20,}=*")),
    ("key assignment", re.compile(r"""(?i)\b(api[_-]?key|secret|password|token)\b["']?\s*[:=]\s*["'][^"'\s{}]{12,}["']""")),
]
INJECTION_PATTERNS = [
    ("override instruction", re.compile(r"(?i)\b(ignore|disregard|forget)\s+(all\s+|any\s+)?(previous|prior|above|earlier|system)\s+(instructions|prompts?|rules)")),
    ("hidden-instruction marker", re.compile(r"(?i)\b(do not|don't|never)\s+(tell|reveal|mention|show)\s+(this|these instructions)\s+to\s+the\s+user")),
    ("exfiltration request", re.compile(r"(?i)\b(send|post|upload|exfiltrate)\b[^.\n]{0,60}\b(credentials?|secrets?|tokens?|api keys?|passwords?)\b[^.\n]{0,60}\bhttps?://")),
    ("invisible characters", re.compile("[\u200b\u200c\u200d\u2060\u202a-\u202e\u2066-\u2069]")),
]
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", re.S)


@dataclass
class Report:
    errors: list[tuple[str, str]] = field(default_factory=list)
    warnings: list[tuple[str, str]] = field(default_factory=list)
    skills: list[dict] = field(default_factory=list)

    def error(self, where: str, msg: str) -> None:
        self.errors.append((where, msg))

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append((where, msg))


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def scan_secrets(text: str, where: str, rep: Report) -> None:
    for label, pat in SECRET_PATTERNS:
        hit = pat.search(text)
        if hit:
            rep.error(f"{where}:{line_of(text, hit.start())}", f"looks like a {label}; skills must not contain credentials")


def check_skill(path: Path, root: Path, rep: Report) -> dict | None:
    where = path.relative_to(root).as_posix()
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        rep.error(where, f"{len(raw) // 1024} KB is over the gateway's 256 KB limit; it won't be scanned")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        rep.error(where, "SKILL.md must be UTF-8")
        return None
    m = FRONTMATTER_RE.match(text)
    if not m:
        rep.error(where, "missing YAML frontmatter between '---' lines at the top")
        return None
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        rep.error(where, f"frontmatter is not valid YAML: {e}")
        return None
    if not isinstance(fm, dict):
        rep.error(where, "frontmatter must be a mapping")
        return None
    extra = sorted(set(fm) - ALLOWED_KEYS)
    if extra:
        rep.error(where, f"frontmatter field(s) {extra} aren't allowed; the gateway would skip this skill")
    name, desc = fm.get("name"), fm.get("description")
    folder = path.parent.name
    if not isinstance(name, str) or not name:
        rep.error(where, "'name' is required")
    else:
        if name != folder:
            rep.error(where, f"name '{name}' must equal the folder name '{folder}'")
        if not NAME_RE.match(name) or len(name) > MAX_NAME:
            rep.error(where, f"name '{name}' must be lowercase words joined by hyphens, at most {MAX_NAME} characters")
    if not isinstance(desc, str) or not desc.strip():
        rep.error(where, "'description' is required: say what the skill does and when to use it")
    elif len(desc) > MAX_DESCRIPTION:
        rep.error(where, f"description is {len(desc)} characters; keep it under {MAX_DESCRIPTION}")
    if "metadata" in fm and not isinstance(fm["metadata"], dict):
        rep.error(where, "'metadata' must be a mapping")
    if not m.group(2).strip():
        rep.error(where, "the skill has no instructions after the frontmatter")

    scan_secrets(text, where, rep)
    for label, pat in INJECTION_PATTERNS:
        hit = pat.search(text)
        if hit:
            rep.error(f"{where}:{line_of(text, hit.start())}", f"possible prompt injection ({label})")

    for ref in re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+)\)", m.group(2)):
        if not (path.parent / ref).exists():
            rep.error(where, f"links to '{ref}', which doesn't exist in the skill folder")

    for f in path.parent.rglob("*"):
        if f.is_file() and f != path and f.suffix in {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".sh", ".ps1"}:
            scan_secrets(f.read_text(encoding="utf-8", errors="replace"), f.relative_to(root).as_posix(), rep)
    return {"name": name or folder, "description": (desc or "").strip(), "path": where,
            "kb": round(len(raw) / 1024, 1)}


def run(root: Path) -> Report:
    rep = Report()
    skills_dir = root / "skills"
    files = sorted(skills_dir.rglob("SKILL.md")) if skills_dir.is_dir() else []
    for p in root.rglob("SKILL.md"):
        if skills_dir not in p.parents and ".git" not in p.parts:
            rep.error(p.relative_to(root).as_posix(), "SKILL.md outside skills/ won't be served (the gateway path is skills/)")
    seen: dict[str, str] = {}
    for p in files:
        info = check_skill(p, root, rep)
        if not info:
            continue
        if info["name"] in seen:
            rep.error(info["path"], f"duplicate skill name, also used by {seen[info['name']]}")
        seen[info["name"]] = info["path"]
        rep.skills.append(info)
    if len(rep.skills) > MAX_SCANNED:
        rep.error("skills", f"{len(rep.skills)} skills; the gateway scans only the first {MAX_SCANNED} per source. "
                            "Split into a second source before adding more.")
    elif len(rep.skills) > MAX_SCANNED - 3:
        rep.warn("skills", f"{len(rep.skills)} of {MAX_SCANNED} scanned slots used")
    return rep


def render(rep: Report) -> str:
    lines = ["## Skills validation", "",
             f"**{len(rep.skills)}** skill(s) · **{len(rep.errors)}** error(s) · **{len(rep.warnings)}** warning(s)",
             "", "| Skill | Size | When to use |", "|---|---|---|"]
    for s in rep.skills:
        desc = s["description"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{s['name']}` | {s['kb']} KB | {desc[:160]}{'…' if len(desc) > 160 else ''} |")
    if rep.errors:
        lines += ["", "### Errors", "", *[f"- `{w}`: {m}" for w, m in rep.errors]]
    if rep.warnings:
        lines += ["", "### Warnings", "", *[f"- `{w}`: {m}" for w, m in rep.warnings]]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    rep = run(args.root.resolve())
    for w, m in rep.errors:
        file, _, line = w.partition(":")
        print(f"::error file={file}{',line=' + line if line else ''}::{m}")
    for w, m in rep.warnings:
        print(f"::warning file={w}::{m}")
    report = render(rep)
    for env in ("GITHUB_STEP_SUMMARY", "VALIDATION_REPORT"):
        if os.environ.get(env):
            with open(os.environ[env], "a", encoding="utf-8") as fh:
                fh.write(report)
    print(report)
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
