#!/usr/bin/env python3
"""Build a batch review packet for the_loop() episodes."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


QA_ARTIFACT_KEYS = ["review_packet", "contact_sheet", "qa_crops", "thumbnail_preview", "lint_report"]


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


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def selected_episodes(tracker: dict, selected_issues: set[str], selected_statuses: set[str]) -> list[dict]:
    episodes = []
    for episode in tracker.get("episodes", []):
        if selected_issues and episode.get("issue") not in selected_issues:
            continue
        if selected_statuses and episode.get("status") not in selected_statuses:
            continue
        episodes.append(episode)
    return episodes


def issue_label(episodes: list[dict]) -> str:
    issues = [episode["issue"] for episode in episodes]
    if not issues:
        return "empty"
    if len(issues) == 1:
        return issues[0]
    return f"{issues[0]}-{issues[-1]}"


def build_thumbnail_preview(production_dir: Path, episodes: list[dict], output: Path) -> None:
    font = load_font(18, bold=True)
    thumb_width = 360
    label_height = 32
    gutter = 16
    margin = 18
    columns = 3
    tiles = []
    for episode in episodes:
        final_path = resolve_path(production_dir, episode.get("assets", {}).get("final"))
        if not final_path or not final_path.exists():
            continue
        image = Image.open(final_path).convert("RGB")
        thumb_height = round(image.height * (thumb_width / image.width))
        thumb = image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_width, label_height + thumb_height), "#f8f4ed")
        draw = ImageDraw.Draw(tile)
        draw.text((8, 5), f"{episode['issue']} {episode['title']}", font=font, fill="#111820")
        tile.paste(thumb, (0, label_height))
        tiles.append(tile)
    if not tiles:
        raise RuntimeError("No thumbnails could be built.")
    rows = (len(tiles) + columns - 1) // columns
    tile_height = max(tile.height for tile in tiles)
    sheet = Image.new(
        "RGB",
        (margin * 2 + columns * thumb_width + (columns - 1) * gutter, margin * 2 + rows * tile_height + (rows - 1) * gutter),
        "#ebe4d8",
    )
    for index, tile in enumerate(tiles):
        row = index // columns
        col = index % columns
        x = margin + col * (thumb_width + gutter)
        y = margin + row * (tile_height + gutter)
        sheet.paste(tile, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def write_review_markdown(path: Path, episodes: list[dict], artifacts: dict[str, str]) -> None:
    lines = [
        "# the_loop() QA Review",
        "",
        f"Generated: {dt.date.today().isoformat()}",
        "",
        "Human approval remains pending. Codex QA only means the files, review artifacts, and metadata are ready for Nick's review.",
        "",
        "## Artifacts",
        "",
    ]
    for key in QA_ARTIFACT_KEYS:
        lines.append(f"- {key}: `{artifacts[key]}`")
    lines.extend(["", "## Episodes", ""])
    for episode in episodes:
        lines.extend(
            [
                f"### {episode['issue']} {episode['title']}",
                "",
                "- [ ] Paige glasses align in every visible face.",
                "- [ ] Laptop screens and back lids make physical sense.",
                "- [ ] Speech balloons are readable and centered.",
                "- [ ] Final panel joke lands cleanly.",
                "- [ ] Easter egg, if present, stays subtle.",
                "- [ ] Approved by Nick.",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_script(script_name: str, args: list[str]) -> subprocess.CompletedProcess[str]:
    script_path = Path(__file__).resolve().parent / script_name
    return subprocess.run([sys.executable, str(script_path), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-dir", type=Path, default=default_production_dir())
    parser.add_argument("--issues", help="Comma-separated issue numbers to include.")
    parser.add_argument("--status", action="append", help="Only include this status. May be repeated.")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    production_dir = args.production_dir.resolve()
    tracker_path = production_dir / "episodes.json"
    tracker = json.loads(tracker_path.read_text(encoding="utf-8"))
    selected = selected_episodes(tracker, parse_issues(args.issues), set(args.status or []))
    if not selected:
        raise SystemExit("No episodes selected for review packet.")

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = args.output_dir or (production_dir / "review-packets" / f"{issue_label(selected)}-{stamp}")
    output_dir.mkdir(parents=True, exist_ok=True)

    contact_sheet = output_dir / "contact-sheet.png"
    qa_crops = output_dir / "qa-crops.png"
    thumbnail_preview = output_dir / "thumbnail-preview.png"
    review_packet = output_dir / "qa-review.md"
    lint_report = output_dir / "lint-report.txt"
    lint_report.write_text("Pending lint run.\n", encoding="utf-8")

    issue_arg = ",".join(episode["issue"] for episode in selected)
    result = run_script(
        "build_contact_sheet.py",
        ["--production-dir", str(production_dir), "--issues", issue_arg, "--output", str(contact_sheet)],
    )
    if result.returncode:
        print(result.stdout)
        return result.returncode
    result = run_script(
        "build_qa_crops.py",
        ["--production-dir", str(production_dir), "--issues", issue_arg, "--output", str(qa_crops), "--columns", "3"],
    )
    if result.returncode:
        print(result.stdout)
        return result.returncode
    build_thumbnail_preview(production_dir, selected, thumbnail_preview)

    artifact_paths = {
        "review_packet": rel_path(production_dir, review_packet),
        "contact_sheet": rel_path(production_dir, contact_sheet),
        "qa_crops": rel_path(production_dir, qa_crops),
        "thumbnail_preview": rel_path(production_dir, thumbnail_preview),
        "lint_report": rel_path(production_dir, lint_report),
    }
    write_review_markdown(review_packet, selected, artifact_paths)

    today = dt.date.today().isoformat()
    for episode in selected:
        episode["status"] = "qa_ready"
        episode.setdefault("qa", {})["status"] = "qa_ready"
        episode["qa_artifacts"] = artifact_paths
        episode.setdefault("approval", {})
        episode["approval"]["codex_qa"] = {
            "status": "passed",
            "date": today,
            "notes": f"Review packet generated at {artifact_paths['review_packet']}.",
        }
        episode["approval"]["human"] = {
            "status": "pending",
            "reviewer": "Nick",
            "date": None,
            "notes": "",
        }
        episode.setdefault("defects", [])
    tracker["updated"] = today
    tracker_path.write_text(json.dumps(tracker, indent=2) + "\n", encoding="utf-8")

    lint_args = ["--production-dir", str(production_dir)]
    for episode in selected:
        lint_args.extend(["--issue", episode["issue"]])
    lint_result = run_script("lint_episode.py", lint_args)
    lint_report.write_text(lint_result.stdout, encoding="utf-8")
    print(f"Saved review packet: {review_packet}")
    print(f"Saved lint report: {lint_report}")
    if lint_result.returncode:
        print(lint_result.stdout)
    return lint_result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
