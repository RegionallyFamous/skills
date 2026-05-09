#!/usr/bin/env python3
"""Migrate the_loop() episodes to canonical asset filenames."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
from pathlib import Path


STATUSES = [
    "idea",
    "scripted",
    "art_draft",
    "lettered",
    "qa_needed",
    "qa_ready",
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


def resolve_path(production_dir: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return (production_dir / path).resolve()


def rel_path(production_dir: Path, path: Path) -> str:
    return os.path.relpath(path.resolve(), production_dir.resolve())


def parse_issues(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def next_backup_path(path: Path) -> Path:
    candidate = path.with_name(f"{path.stem}-precanonical{path.suffix}")
    index = 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}-precanonical-{index}{path.suffix}")
        index += 1
    return candidate


def safe_copy(source: Path, destination: Path, dry_run: bool) -> Path | None:
    backup = None
    if destination.exists() and destination.resolve() != source.resolve():
        backup = next_backup_path(destination)
        if not dry_run:
            shutil.copy2(destination, backup)
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.resolve() != source.resolve():
            shutil.copy2(source, destination)
    return backup


def ensure_variant(episode: dict, variant: dict) -> None:
    variants = episode.setdefault("review_variants", [])
    if not isinstance(variants, list):
        variants = []
    variants = [item for item in variants if item.get("name") != variant["name"]]
    variants.append(variant)
    episode["review_variants"] = variants


def pending_artifacts() -> dict:
    return {
        "review_packet": None,
        "contact_sheet": None,
        "qa_crops": None,
        "thumbnail_preview": None,
        "lint_report": None,
    }


def pending_approval() -> dict:
    return {
        "codex_qa": {
            "status": "pending",
            "date": None,
            "notes": "Canonical migration complete; awaiting review packet.",
        },
        "human": {
            "status": "pending",
            "reviewer": "Nick",
            "date": None,
            "notes": "",
        },
    }


def manual_repair_defect(production_dir: Path) -> dict:
    return {
        "area": "paige_glasses",
        "severity": "blocker",
        "description": "Panel 3 Paige glasses drifted below her eyes in the previous approved final.",
        "status": "resolved",
        "resolution_method": "manual_repair_exception",
        "resolution_notes": "Used normalized art as the base, redrew only the panel 3 glasses, relettered, and generated before/after crop sheets.",
        "before": "../comics/001-cache-me-if-you-can/the_loop-001-cache-me-if-you-can-glasses-crops-before.png",
        "after": "../comics/001-cache-me-if-you-can/the_loop-001-cache-me-if-you-can-glasses-crops-fixed.png",
    }


def migrate_episode(production_dir: Path, episode: dict, dry_run: bool) -> list[str]:
    issue = episode["issue"]
    slug = episode["slug"]
    messages: list[str] = []
    folder = resolve_path(production_dir, episode.get("assets", {}).get("folder"))
    if not folder:
        raise RuntimeError(f"{issue}: missing folder path")

    old_assets = dict(episode.get("assets", {}))
    source_art = resolve_path(production_dir, old_assets.get("art"))
    source_lettering = resolve_path(production_dir, old_assets.get("lettering"))
    source_final = resolve_path(production_dir, old_assets.get("final"))
    for label, path in [("art", source_art), ("lettering", source_lettering), ("final", source_final)]:
        if not path or not path.exists():
            raise RuntimeError(f"{issue}: source {label} missing: {path}")

    canonical = {
        "folder": folder,
        "art": folder / f"the_loop-{issue}-{slug}-art.png",
        "lettering": folder / f"the_loop-{issue}-{slug}-lettering.json",
        "final": folder / f"the_loop-{issue}-{slug}-final.png",
    }

    legacy_variant = {
        "name": "legacy-current-before-canonical-migration",
        "art": old_assets.get("art"),
        "lettering": old_assets.get("lettering"),
        "final": old_assets.get("final"),
        "notes": "Assets tracked before canonical filename migration.",
    }
    ensure_variant(episode, legacy_variant)

    backups = {}
    for label, source in [("art", source_art), ("lettering", source_lettering), ("final", source_final)]:
        backup = safe_copy(source, canonical[label], dry_run)
        if backup:
            backups[label] = rel_path(production_dir, backup)
            messages.append(f"{issue}: preserved existing canonical {label} as {backup.name}")
        messages.append(f"{issue}: {'would copy' if dry_run else 'copied'} {source.name} -> {canonical[label].name}")

    if backups:
        ensure_variant(
            episode,
            {
                "name": "precanonical-overwritten-assets",
                **backups,
                "notes": "Files that previously occupied canonical filenames before migration overwrote them.",
            },
        )

    episode["assets"] = {
        "folder": rel_path(production_dir, folder),
        "art": rel_path(production_dir, canonical["art"]),
        "lettering": rel_path(production_dir, canonical["lettering"]),
        "final": rel_path(production_dir, canonical["final"]),
    }
    if episode.get("status") in {"approved", "published", "qa_ready"}:
        episode["status"] = "qa_needed"
    episode["qa_artifacts"] = pending_artifacts()
    episode["approval"] = pending_approval()
    episode.setdefault("defects", [])
    if issue == "001" and not any(
        item.get("area") == "paige_glasses" and item.get("resolution_method") == "manual_repair_exception"
        for item in episode["defects"]
    ):
        episode["defects"].append(manual_repair_defect(production_dir))
    episode["qa"]["status"] = "qa_needed"
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-dir", type=Path, default=default_production_dir())
    parser.add_argument("--issues", help="Comma-separated issue numbers to migrate. Defaults to all.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    production_dir = args.production_dir.resolve()
    tracker_path = production_dir / "episodes.json"
    tracker = json.loads(tracker_path.read_text(encoding="utf-8"))
    tracker["statuses"] = STATUSES
    tracker["updated"] = dt.date.today().isoformat()
    selected = parse_issues(args.issues)

    messages: list[str] = []
    for episode in tracker.get("episodes", []):
        if selected and episode.get("issue") not in selected:
            continue
        messages.extend(migrate_episode(production_dir, episode, args.dry_run))

    for message in messages:
        print(message)
    if args.dry_run:
        print("No files written (--dry-run).")
        return 0

    tracker_path.write_text(json.dumps(tracker, indent=2) + "\n", encoding="utf-8")
    print(f"Updated tracker: {tracker_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
