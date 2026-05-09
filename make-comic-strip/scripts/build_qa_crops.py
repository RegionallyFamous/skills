#!/usr/bin/env python3
"""Build crop sheets for face, laptop, and lettering QA."""

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


def crop_box(width: int, height: int, panel: int, rel_box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    panel_width = width / 4
    left = panel_width * panel
    x1, y1, x2, y2 = rel_box
    return (
        round(left + panel_width * x1),
        round(height * y1),
        round(left + panel_width * x2),
        round(height * y2),
    )


def make_tile(
    image: Image.Image,
    label: str,
    tile_size: tuple[int, int],
    font: ImageFont.ImageFont,
    cover: bool = False,
) -> Image.Image:
    label_height = 28
    tile = Image.new("RGB", tile_size, "#f8f4ed")
    draw = ImageDraw.Draw(tile)
    draw.text((8, 5), label, fill="#111820", font=font)
    content_box = (0, label_height, tile_size[0], tile_size[1])
    target_size = (tile_size[0], tile_size[1] - label_height)
    if cover:
        fitted = ImageOps.fit(image.convert("RGB"), target_size, Image.Resampling.LANCZOS, centering=(0.5, 0.42))
    else:
        fitted = ImageOps.contain(image.convert("RGB"), target_size, Image.Resampling.LANCZOS)
    x = (tile_size[0] - fitted.width) // 2
    y = label_height + (tile_size[1] - label_height - fitted.height) // 2
    tile.paste(fitted, (x, y))
    draw.rectangle(content_box, outline="#c8bca8", width=1)
    return tile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-dir", type=Path, default=default_production_dir())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--issues", help="Comma-separated issue numbers to include.")
    parser.add_argument("--columns", type=int, default=3)
    parser.add_argument("--tile-width", type=int, default=420)
    parser.add_argument("--tile-height", type=int, default=220)
    args = parser.parse_args()

    production_dir = args.production_dir.resolve()
    tracker = json.loads((production_dir / "episodes.json").read_text(encoding="utf-8"))
    selected_issues = parse_issues(args.issues)
    font = load_font(16, bold=True)

    crop_specs = [
        ("face", 0, (0.02, 0.10, 0.66, 0.70), True),
        ("laptop", 0, (0.14, 0.30, 0.92, 0.92), True),
        ("lettering", 0, (0.00, 0.00, 1.00, 0.48), False),
    ]

    tiles = []
    for episode in tracker.get("episodes", []):
        issue = str(episode.get("issue"))
        if selected_issues and issue not in selected_issues:
            continue
        final_path = resolve_path(production_dir, episode.get("assets", {}).get("final", ""))
        if not final_path.exists():
            continue
        image = Image.open(final_path).convert("RGB")
        for kind, panel, rel_box, cover in crop_specs:
            box = crop_box(image.width, image.height, panel, rel_box)
            crop = image.crop(box)
            label = f"{issue} {kind}"
            tiles.append(make_tile(crop, label, (args.tile_width, args.tile_height), font, cover=cover))

    if not tiles:
        raise SystemExit("No final images found for QA crop sheet.")

    columns = max(1, args.columns)
    gutter = 18
    margin = 20
    rows = (len(tiles) + columns - 1) // columns
    sheet_width = margin * 2 + columns * args.tile_width + (columns - 1) * gutter
    sheet_height = margin * 2 + rows * args.tile_height + (rows - 1) * gutter
    sheet = Image.new("RGB", (sheet_width, sheet_height), "#ebe4d8")

    for index, tile in enumerate(tiles):
        row = index // columns
        col = index % columns
        x = margin + col * (args.tile_width + gutter)
        y = margin + row * (args.tile_height + gutter)
        sheet.paste(tile, (x, y))

    output = args.output or (production_dir / "qa-crops.png")
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(f"Saved QA crop sheet: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
