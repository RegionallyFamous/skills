#!/usr/bin/env python3
"""Create the next the_loop() episode folder and starter metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path


STATUSES = [
    "idea",
    "scripted",
    "art_draft",
    "lettered",
    "qa_needed",
    "approved",
    "published",
    "retired",
]


def default_production_dir() -> Path:
    cwd = Path.cwd()
    candidates = [
        cwd / "outputs" / "the_loop" / "production",
        cwd / "production",
        Path.home() / "Documents" / "Projects" / "WordPress.org" / "outputs" / "the_loop" / "production",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def slugify(value: str) -> str:
    value = value.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "untitled-episode"


def load_tracker(production_dir: Path) -> dict:
    tracker_path = production_dir / "episodes.json"
    if not tracker_path.exists():
        return {
            "schema_version": "1.0",
            "series": "the_loop()",
            "updated": dt.date.today().isoformat(),
            "statuses": STATUSES,
            "episodes": [],
        }
    return json.loads(tracker_path.read_text(encoding="utf-8"))


def render_template(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def next_issue(episodes: list[dict]) -> str:
    numbers = []
    for episode in episodes:
        issue = str(episode.get("issue", "")).strip()
        if issue.isdigit():
            numbers.append(int(issue))
    return f"{(max(numbers) if numbers else 0) + 1:03d}"


def make_entry(issue: str, slug: str, title: str, premise: str, easter_egg: str) -> dict:
    folder = f"../comics/{issue}-{slug}"
    return {
        "issue": issue,
        "slug": slug,
        "title": title,
        "status": "idea",
        "premise": premise,
        "script_beats": [
            "Panel 1 setup to draft.",
            "Panel 2 complication to draft.",
            "Panel 3 escalation to draft.",
            "Panel 4 turn to draft.",
        ],
        "assets": {
            "folder": folder,
            "art": f"{folder}/the_loop-{issue}-{slug}-art.png",
            "lettering": f"{folder}/the_loop-{issue}-{slug}-lettering.json",
            "final": f"{folder}/the_loop-{issue}-{slug}-final.png",
        },
        "qa": {
            "paige_glasses": "required",
            "laptop_screen_direction": "required",
            "generated_text": "no generated readable text",
            "lettering": "pending",
            "status": "pending",
        },
        "easter_eggs": [easter_egg] if easter_egg else [],
        "publication": {
            "date": None,
            "url": None,
            "notes": "",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-dir", type=Path, default=default_production_dir())
    parser.add_argument("--title", default="Untitled Episode")
    parser.add_argument("--slug")
    parser.add_argument("--premise", default="One clear WordPress workflow moment to draft.")
    parser.add_argument("--easter-egg", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Allow writing into an existing empty episode folder.")
    args = parser.parse_args()

    production_dir = args.production_dir.resolve()
    tracker = load_tracker(production_dir)
    episodes = tracker.setdefault("episodes", [])
    issue = next_issue(episodes)
    slug = slugify(args.slug or args.title)
    folder = (production_dir / ".." / "comics" / f"{issue}-{slug}").resolve()
    brief_path = folder / "strip-brief.md"
    local_episode_path = folder / "episode.json"

    existing_issues = {str(ep.get("issue")) for ep in episodes}
    existing_slugs = {str(ep.get("slug")) for ep in episodes}
    if issue in existing_issues:
        print(f"error: issue {issue} already exists", file=sys.stderr)
        return 1
    if slug in existing_slugs:
        print(f"error: slug {slug!r} already exists", file=sys.stderr)
        return 1

    entry = make_entry(issue, slug, args.title, args.premise, args.easter_egg)
    replacements = {
        "ISSUE": issue,
        "SLUG": slug,
        "TITLE": args.title,
        "PREMISE": args.premise,
        "PANEL_1": "establish the WordPress task",
        "PANEL_2": "show the first complication",
        "PANEL_3": "escalate the workflow surprise",
        "PANEL_4": "land the final turn",
        "EASTER_EGG_ID": args.easter_egg or "optional-subtle-detail",
    }

    skill_dir = Path(__file__).resolve().parents[1]
    brief_template = (skill_dir / "templates" / "strip-brief.md").read_text(encoding="utf-8")
    brief = render_template(brief_template, replacements)

    print(f"Next issue: {issue}")
    print(f"Slug: {slug}")
    print(f"Episode folder: {folder}")
    print(f"Tracker: {production_dir / 'episodes.json'}")
    print(f"Brief: {brief_path}")

    if args.dry_run:
        print("No files written (--dry-run).")
        return 0

    if folder.exists() and not args.force:
        print(f"error: folder already exists: {folder}", file=sys.stderr)
        return 1

    production_dir.mkdir(parents=True, exist_ok=True)
    folder.mkdir(parents=True, exist_ok=True)
    tracker["updated"] = dt.date.today().isoformat()
    tracker["statuses"] = tracker.get("statuses") or STATUSES
    episodes.append(entry)
    (production_dir / "episodes.json").write_text(json.dumps(tracker, indent=2) + "\n", encoding="utf-8")
    brief_path.write_text(brief, encoding="utf-8")
    local_episode_path.write_text(json.dumps(entry, indent=2) + "\n", encoding="utf-8")
    print("Created episode starter files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
