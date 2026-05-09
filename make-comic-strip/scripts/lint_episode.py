#!/usr/bin/env python3
"""Lint the_loop() production episode metadata."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path


DEFAULT_STATUSES = {
    "idea",
    "scripted",
    "art_draft",
    "lettered",
    "qa_needed",
    "approved",
    "published",
    "retired",
}
MATERIALIZED_STATUSES = {"art_draft", "lettered", "qa_needed", "approved", "published"}
LETTERED_STATUSES = {"lettered", "qa_needed", "approved", "published"}
APPROVED_STATUSES = {"approved", "published"}


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


def resolve_path(production_dir: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return (production_dir / path).resolve()


def add_error(errors: list[str], episode_id: str, message: str) -> None:
    errors.append(f"{episode_id}: {message}")


def validate_episode(production_dir: Path, episode: dict, statuses: set[str], errors: list[str]) -> None:
    issue = str(episode.get("issue", "")).strip()
    slug = str(episode.get("slug", "")).strip()
    episode_id = issue or slug or "<unknown>"

    for field in ["issue", "slug", "title", "status", "premise", "script_beats", "assets", "qa", "publication"]:
        if field not in episode:
            add_error(errors, episode_id, f"missing required field: {field}")

    if not re.fullmatch(r"\d{3}", issue):
        add_error(errors, episode_id, "issue must be a three-digit string")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        add_error(errors, episode_id, "slug must be lowercase kebab-case")

    status = str(episode.get("status", "")).strip()
    if status not in statuses:
        add_error(errors, episode_id, f"invalid status: {status!r}")

    beats = episode.get("script_beats")
    if not isinstance(beats, list) or len(beats) != 4:
        add_error(errors, episode_id, "script_beats must contain exactly four panel beats")
    elif status in {"scripted", "art_draft", "lettered", "qa_needed", "approved", "published"}:
        for index, beat in enumerate(beats, start=1):
            if not str(beat).strip():
                add_error(errors, episode_id, f"script beat {index} is empty")

    assets = episode.get("assets") if isinstance(episode.get("assets"), dict) else {}
    for field in ["folder", "art", "lettering", "final"]:
        if not assets.get(field):
            add_error(errors, episode_id, f"missing asset path: {field}")

    folder_path = resolve_path(production_dir, assets.get("folder"))
    art_path = resolve_path(production_dir, assets.get("art"))
    lettering_path = resolve_path(production_dir, assets.get("lettering"))
    final_path = resolve_path(production_dir, assets.get("final"))

    expected_folder = f"{issue}-{slug}" if issue and slug else ""
    if folder_path and expected_folder and folder_path.name != expected_folder:
        add_error(errors, episode_id, f"folder should be named {expected_folder}")

    if status in MATERIALIZED_STATUSES:
        if folder_path and not folder_path.exists():
            add_error(errors, episode_id, f"episode folder does not exist: {folder_path}")
        if art_path and not art_path.exists():
            add_error(errors, episode_id, f"art image does not exist: {art_path}")
    if status in LETTERED_STATUSES:
        if lettering_path and not lettering_path.exists():
            add_error(errors, episode_id, f"lettering spec does not exist: {lettering_path}")
        if final_path and not final_path.exists():
            add_error(errors, episode_id, f"final image does not exist: {final_path}")

    if final_path:
        expected_prefix = f"the_loop-{issue}-{slug}-final"
        if not final_path.name.startswith(expected_prefix) or final_path.suffix.lower() != ".png":
            add_error(errors, episode_id, f"final filename should start with {expected_prefix} and end in .png")
    if lettering_path:
        expected_lettering = f"the_loop-{issue}-{slug}-lettering.json"
        if lettering_path.name not in {expected_lettering, "lettering-spec.json"}:
            add_error(errors, episode_id, f"lettering spec should be {expected_lettering} or lettering-spec.json")

    qa = episode.get("qa") if isinstance(episode.get("qa"), dict) else {}
    if not qa:
        add_error(errors, episode_id, "missing qa object")
    paige_glasses = qa.get("paige_glasses")
    if paige_glasses not in {"required", "planned", "verified", "not_applicable"}:
        add_error(errors, episode_id, "missing Paige glasses requirement or verification")
    elif status in APPROVED_STATUSES and paige_glasses != "verified":
        add_error(errors, episode_id, "approved episodes must verify Paige glasses")

    laptop_note = qa.get("laptop_screen_direction")
    if laptop_note not in {"required", "planned", "verified", "not_applicable"}:
        add_error(errors, episode_id, "missing laptop screen direction note")
    elif status in APPROVED_STATUSES and laptop_note != "verified":
        add_error(errors, episode_id, "approved episodes must verify laptop screen direction")

    if not qa.get("generated_text"):
        add_error(errors, episode_id, "missing generated-text QA note")
    if not qa.get("lettering"):
        add_error(errors, episode_id, "missing lettering QA note")
    if not qa.get("status"):
        add_error(errors, episode_id, "missing QA status")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-dir", type=Path, default=default_production_dir())
    parser.add_argument("--issue", action="append", help="Limit linting to one issue. May be repeated.")
    args = parser.parse_args()

    production_dir = args.production_dir.resolve()
    tracker_path = production_dir / "episodes.json"
    if not tracker_path.exists():
        print(f"error: missing tracker: {tracker_path}", file=sys.stderr)
        return 1

    tracker = json.loads(tracker_path.read_text(encoding="utf-8"))
    episodes = tracker.get("episodes", [])
    statuses = set(tracker.get("statuses") or DEFAULT_STATUSES)
    selected_issues = set(args.issue or [])
    if selected_issues:
        episodes = [episode for episode in episodes if str(episode.get("issue")) in selected_issues]

    errors: list[str] = []
    issue_counts = Counter(str(episode.get("issue")) for episode in tracker.get("episodes", []))
    slug_counts = Counter(str(episode.get("slug")) for episode in tracker.get("episodes", []))
    for issue, count in sorted(issue_counts.items()):
        if issue and count > 1:
            errors.append(f"tracker: duplicate issue number: {issue}")
    for slug, count in sorted(slug_counts.items()):
        if slug and count > 1:
            errors.append(f"tracker: duplicate slug: {slug}")

    for episode in episodes:
        validate_episode(production_dir, episode, statuses, errors)

    if errors:
        print(f"Found {len(errors)} issue(s):")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"OK: {len(episodes)} episode(s) passed lint in {tracker_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
