#!/usr/bin/env python3
"""Build a contact sheet from final the_loop() episode images."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


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


def resolve_path(production_dir: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (production_dir / path).resolve()


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


def parse_issues(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-dir", type=Path, default=default_production_dir())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--issues", help="Comma-separated issue numbers to include.")
    parser.add_argument("--status", action="append", help="Only include this status. May be repeated.")
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--thumb-width", type=int, default=760)
    args = parser.parse_args()

    production_dir = args.production_dir.resolve()
    tracker = json.loads((production_dir / "episodes.json").read_text(encoding="utf-8"))
    selected_issues = parse_issues(args.issues)
    selected_statuses = set(args.status or [])

    episodes = []
    for episode in tracker.get("episodes", []):
        if selected_issues and str(episode.get("issue")) not in selected_issues:
            continue
        if selected_statuses and episode.get("status") not in selected_statuses:
            continue
        final_path = resolve_path(production_dir, episode.get("assets", {}).get("final", ""))
        if final_path.exists():
            episodes.append((episode, final_path))

    if not episodes:
        raise SystemExit("No final images found for contact sheet.")

    columns = max(1, args.columns)
    thumb_width = max(240, args.thumb_width)
    label_height = 42
    gutter = 24
    margin = 24
    font = load_font(22, bold=True)
    small_font = load_font(16)

    tiles = []
    for episode, final_path in episodes:
        image = Image.open(final_path).convert("RGB")
        thumb_height = round(image.height * (thumb_width / image.width))
        thumb = image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_width, label_height + thumb_height), "#f7f3eb")
        draw = ImageDraw.Draw(tile)
        label = f"{episode['issue']}  {episode['title']}"
        draw.text((12, 7), label, fill="#111820", font=font)
        draw.text((12, 28), episode.get("status", ""), fill="#5f6670", font=small_font)
        tile.paste(thumb, (0, label_height))
        tiles.append(tile)

    rows = (len(tiles) + columns - 1) // columns
    tile_width = thumb_width
    tile_height = max(tile.height for tile in tiles)
    sheet_width = margin * 2 + columns * tile_width + (columns - 1) * gutter
    sheet_height = margin * 2 + rows * tile_height + (rows - 1) * gutter
    sheet = Image.new("RGB", (sheet_width, sheet_height), "#ebe4d8")

    for index, tile in enumerate(tiles):
        row = index // columns
        col = index % columns
        x = margin + col * (tile_width + gutter)
        y = margin + row * (tile_height + gutter)
        sheet.paste(tile, (x, y))

    output = args.output or (production_dir / "contact-sheet.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(f"Saved contact sheet: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
