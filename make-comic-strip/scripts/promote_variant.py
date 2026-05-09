#!/usr/bin/env python3
"""Promote regenerated candidate assets to canonical the_loop() episode assets."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


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


def copy_candidate(source: Path, destination: Path) -> None:
    if not source.exists():
        raise RuntimeError(f"candidate does not exist: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-dir", type=Path, default=default_production_dir())
    parser.add_argument("--issue", required=True)
    parser.add_argument("--art", type=Path)
    parser.add_argument("--lettering", type=Path)
    parser.add_argument("--final", type=Path, required=True)
    parser.add_argument("--variant-name", default="previous-canonical-before-promotion")
    parser.add_argument("--notes", default="Previous canonical assets archived before candidate promotion.")
    args = parser.parse_args()

    production_dir = args.production_dir.resolve()
    tracker_path = production_dir / "episodes.json"
    tracker = json.loads(tracker_path.read_text(encoding="utf-8"))
    episode = next((item for item in tracker.get("episodes", []) if item.get("issue") == args.issue), None)
    if not episode:
        raise SystemExit(f"No episode found for issue {args.issue}")

    issue = episode["issue"]
    slug = episode["slug"]
    folder = resolve_path(production_dir, episode.get("assets", {}).get("folder"))
    if not folder:
        raise SystemExit(f"{issue}: missing folder")

    current_assets = dict(episode.get("assets", {}))
    variants = episode.setdefault("review_variants", [])
    variants = [item for item in variants if item.get("name") != args.variant_name]
    variants.append(
        {
            "name": args.variant_name,
            "art": current_assets.get("art"),
            "lettering": current_assets.get("lettering"),
            "final": current_assets.get("final"),
            "notes": args.notes,
        }
    )
    episode["review_variants"] = variants

    canonical_art = folder / f"the_loop-{issue}-{slug}-art.png"
    canonical_lettering = folder / f"the_loop-{issue}-{slug}-lettering.json"
    canonical_final = folder / f"the_loop-{issue}-{slug}-final.png"

    art_source = args.art or resolve_path(production_dir, current_assets.get("art"))
    lettering_source = args.lettering or resolve_path(production_dir, current_assets.get("lettering"))
    final_source = args.final
    copy_candidate(art_source, canonical_art)  # type: ignore[arg-type]
    copy_candidate(lettering_source, canonical_lettering)  # type: ignore[arg-type]
    copy_candidate(final_source, canonical_final)

    episode["assets"] = {
        "folder": rel_path(production_dir, folder),
        "art": rel_path(production_dir, canonical_art),
        "lettering": rel_path(production_dir, canonical_lettering),
        "final": rel_path(production_dir, canonical_final),
    }
    episode["status"] = "qa_needed"
    episode["qa_artifacts"] = {
        "review_packet": None,
        "contact_sheet": None,
        "qa_crops": None,
        "thumbnail_preview": None,
        "lint_report": None,
    }
    episode["approval"] = {
        "codex_qa": {
            "status": "pending",
            "date": None,
            "notes": "Candidate promoted; new review packet required.",
        },
        "human": {
            "status": "pending",
            "reviewer": "Nick",
            "date": None,
            "notes": "",
        },
    }
    episode.setdefault("qa", {})["status"] = "qa_needed"
    tracker["updated"] = dt.date.today().isoformat()
    tracker_path.write_text(json.dumps(tracker, indent=2) + "\n", encoding="utf-8")

    lint_script = Path(__file__).resolve().parent / "lint_episode.py"
    result = subprocess.run(
        [sys.executable, str(lint_script), "--production-dir", str(production_dir), "--issue", issue],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(result.stdout)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
