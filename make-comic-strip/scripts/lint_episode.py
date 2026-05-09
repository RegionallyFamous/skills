#!/usr/bin/env python3
"""Lint the_loop() production episode metadata."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from PIL import Image


STATUSES = {
    "idea",
    "scripted",
    "art_draft",
    "lettered",
    "qa_needed",
    "qa_ready",
    "approved",
    "published",
    "retired",
}
MATERIALIZED_STATUSES = {"art_draft", "lettered", "qa_needed", "qa_ready", "approved", "published"}
LETTERED_STATUSES = {"lettered", "qa_needed", "qa_ready", "approved", "published"}
CANONICAL_STATUSES = {"qa_needed", "qa_ready", "approved", "published"}
QA_ARTIFACT_STATUSES = {"qa_ready", "approved", "published"}
HUMAN_APPROVAL_STATUSES = {"approved", "published"}
CODEX_QA_STATUSES = {"pending", "passed", "failed"}
HUMAN_STATUSES = {"pending", "approved", "rejected"}
DEFECT_CLOSED_STATUSES = {"resolved", "accepted_exception"}
QA_ARTIFACT_KEYS = ["review_packet", "contact_sheet", "qa_crops", "thumbnail_preview", "lint_report"]
EXPECTED_SIZE = (2172, 724)


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


def check_required_object(errors: list[str], episode_id: str, parent: dict, field: str) -> dict:
    value = parent.get(field)
    if not isinstance(value, dict):
        add_error(errors, episode_id, f"missing required object: {field}")
        return {}
    return value


def check_path_exists(
    production_dir: Path,
    errors: list[str],
    episode_id: str,
    label: str,
    value: str | None,
) -> Path | None:
    path = resolve_path(production_dir, value)
    if not value:
        add_error(errors, episode_id, f"missing path: {label}")
        return None
    if path and not path.exists():
        add_error(errors, episode_id, f"{label} does not exist: {path}")
    return path


def validate_approval(episode: dict, status: str, episode_id: str, errors: list[str]) -> None:
    approval = check_required_object(errors, episode_id, episode, "approval")
    codex_qa = approval.get("codex_qa") if isinstance(approval.get("codex_qa"), dict) else {}
    human = approval.get("human") if isinstance(approval.get("human"), dict) else {}
    if not codex_qa:
        add_error(errors, episode_id, "missing approval.codex_qa object")
    if not human:
        add_error(errors, episode_id, "missing approval.human object")

    codex_status = codex_qa.get("status")
    if codex_status not in CODEX_QA_STATUSES:
        add_error(errors, episode_id, "approval.codex_qa.status must be pending, passed, or failed")
    if status in QA_ARTIFACT_STATUSES and codex_status != "passed":
        add_error(errors, episode_id, "qa_ready/approved episodes require approval.codex_qa.status=passed")
    if codex_status == "passed" and not codex_qa.get("date"):
        add_error(errors, episode_id, "passed Codex QA requires approval.codex_qa.date")

    human_status = human.get("status")
    if human_status not in HUMAN_STATUSES:
        add_error(errors, episode_id, "approval.human.status must be pending, approved, or rejected")
    if human.get("reviewer") != "Nick":
        add_error(errors, episode_id, "approval.human.reviewer must be Nick")
    if status in HUMAN_APPROVAL_STATUSES:
        if human_status != "approved":
            add_error(errors, episode_id, "approved/published episodes require explicit human approval")
        if not human.get("date"):
            add_error(errors, episode_id, "approved/published episodes require approval.human.date")


def validate_defects(production_dir: Path, episode: dict, status: str, episode_id: str, errors: list[str]) -> None:
    defects = episode.get("defects")
    if not isinstance(defects, list):
        add_error(errors, episode_id, "defects must be a list")
        return
    for index, defect in enumerate(defects, start=1):
        label = f"defect {index}"
        if not isinstance(defect, dict):
            add_error(errors, episode_id, f"{label} must be an object")
            continue
        for field in ["area", "severity", "description", "status"]:
            if not defect.get(field):
                add_error(errors, episode_id, f"{label} missing {field}")
        defect_status = defect.get("status")
        if status in QA_ARTIFACT_STATUSES and defect_status not in DEFECT_CLOSED_STATUSES:
            add_error(errors, episode_id, f"{label} is still open")
        if defect.get("resolution_method") == "manual_repair_exception":
            before = check_path_exists(production_dir, errors, episode_id, f"{label} before artifact", defect.get("before"))
            after = check_path_exists(production_dir, errors, episode_id, f"{label} after artifact", defect.get("after"))
            if before and after and before == after:
                add_error(errors, episode_id, f"{label} manual repair before/after artifacts must differ")


def validate_episode(production_dir: Path, episode: dict, statuses: set[str], errors: list[str]) -> None:
    issue = str(episode.get("issue", "")).strip()
    slug = str(episode.get("slug", "")).strip()
    episode_id = issue or slug or "<unknown>"

    for field in [
        "issue",
        "slug",
        "title",
        "status",
        "premise",
        "script_beats",
        "assets",
        "qa",
        "qa_artifacts",
        "approval",
        "defects",
        "publication",
    ]:
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
    elif status in {"scripted", "art_draft", "lettered", "qa_needed", "qa_ready", "approved", "published"}:
        for index, beat in enumerate(beats, start=1):
            if not str(beat).strip():
                add_error(errors, episode_id, f"script beat {index} is empty")

    assets = check_required_object(errors, episode_id, episode, "assets")
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

    if status in CANONICAL_STATUSES:
        expected_names = {
            "art": f"the_loop-{issue}-{slug}-art.png",
            "lettering": f"the_loop-{issue}-{slug}-lettering.json",
            "final": f"the_loop-{issue}-{slug}-final.png",
        }
        for field, expected_name in expected_names.items():
            path = resolve_path(production_dir, assets.get(field))
            if path and path.name != expected_name:
                add_error(errors, episode_id, f"{field} filename must be canonical: {expected_name}")

    if final_path and final_path.exists() and status in LETTERED_STATUSES:
        with Image.open(final_path) as image:
            if image.size != EXPECTED_SIZE:
                add_error(errors, episode_id, f"final image must be {EXPECTED_SIZE[0]}x{EXPECTED_SIZE[1]}, got {image.width}x{image.height}")

    qa = check_required_object(errors, episode_id, episode, "qa")
    paige_glasses = qa.get("paige_glasses")
    if paige_glasses not in {"required", "planned", "verified", "not_applicable"}:
        add_error(errors, episode_id, "missing Paige glasses requirement or verification")
    elif status in QA_ARTIFACT_STATUSES and paige_glasses != "verified":
        add_error(errors, episode_id, "qa_ready/approved episodes must verify Paige glasses")

    laptop_note = qa.get("laptop_screen_direction")
    if laptop_note not in {"required", "planned", "verified", "not_applicable"}:
        add_error(errors, episode_id, "missing laptop screen direction note")
    elif status in QA_ARTIFACT_STATUSES and laptop_note != "verified":
        add_error(errors, episode_id, "qa_ready/approved episodes must verify laptop screen direction")

    if not qa.get("generated_text"):
        add_error(errors, episode_id, "missing generated-text QA note")
    if not qa.get("lettering"):
        add_error(errors, episode_id, "missing lettering QA note")
    if not qa.get("status"):
        add_error(errors, episode_id, "missing QA status")

    qa_artifacts = check_required_object(errors, episode_id, episode, "qa_artifacts")
    if status in QA_ARTIFACT_STATUSES:
        for key in QA_ARTIFACT_KEYS:
            check_path_exists(production_dir, errors, episode_id, f"qa_artifacts.{key}", qa_artifacts.get(key))

    validate_approval(episode, status, episode_id, errors)
    validate_defects(production_dir, episode, status, episode_id, errors)


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
    statuses = set(tracker.get("statuses") or STATUSES)
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

    unknown_statuses = statuses - STATUSES
    if unknown_statuses:
        errors.append(f"tracker: unknown statuses configured: {', '.join(sorted(unknown_statuses))}")
    missing_statuses = STATUSES - statuses
    if missing_statuses:
        errors.append(f"tracker: required statuses missing: {', '.join(sorted(missing_statuses))}")

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
