#!/usr/bin/env python3
"""Letter a comic strip with deterministic masthead and speech balloons."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


DEFAULT_DIALOGUE_FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
DEFAULT_FALLBACK_FONT = "/System/Library/Fonts/Supplemental/Comic Sans MS Bold.ttf"
DEFAULT_TITLE_FONT = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
SKILL_DIR = Path(__file__).resolve().parents[1]


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype(DEFAULT_FALLBACK_FONT, size)


def resolve_skill_path(path: str) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate
    skill_relative = SKILL_DIR / candidate
    if skill_relative.exists():
        return skill_relative
    return candidate


def scaled_box(values: Iterable[float], width: int, height: int) -> tuple[int, ...]:
    vals = list(values)
    out: list[int] = []
    for i, value in enumerate(vals):
        axis = width if i % 2 == 0 else height
        out.append(round(value * axis) if 0 <= value <= 1 else round(value))
    return tuple(out)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0]


def text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[3] - box[1]


def lines_height(draw: ImageDraw.ImageDraw, lines: list[str], font: ImageFont.FreeTypeFont, leading: int) -> int:
    if not lines:
        return 0
    return sum(text_height(draw, line, font) for line in lines) + leading * (len(lines) - 1)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    forced_lines: list[str] = []
    for segment in text.splitlines() or [text]:
        forced_lines.extend(wrap_segment(draw, segment, font, max_width))
    return forced_lines


def wrap_segment(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    font_path: str,
    max_size: int,
    min_size: int,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(max_size, min_size - 1, -1):
        font = load_font(font_path, size)
        lines = wrap_text(draw, text, font, max_width)
        leading = round(size * 0.18)
        if lines_height(draw, lines, font, leading) <= max_height and all(text_width(draw, line, font) <= max_width for line in lines):
            return font, lines, leading
    font = load_font(font_path, min_size)
    return font, wrap_text(draw, text, font, max_width), round(min_size * 0.18)


def draw_balloon(
    draw: ImageDraw.ImageDraw,
    image_size: tuple[int, int],
    item: dict,
    dialogue_font: str,
    bold_font: str,
) -> None:
    width, height = image_size
    x1, y1, x2, y2 = scaled_box(item["box"], width, height)
    fill = tuple(item.get("fill", [255, 255, 255, 248]))
    outline = tuple(item.get("outline", [18, 18, 18, 255]))
    stroke = int(item.get("stroke", 4))
    radius = int(item.get("radius", 20))
    tail = item.get("tail")

    if tail:
        tx, ty = scaled_box(tail, width, height)
        mid = (x1 + x2) // 2
        tail_half_width = int(item.get("tail_width", 24))
        triangle = [(mid - tail_half_width, y2 - 2), (mid + tail_half_width, y2 - 2), (tx, ty)]
        draw.polygon(triangle, fill=fill)
        draw.line(triangle + [triangle[0]], fill=outline, width=stroke)

    draw.rounded_rectangle((x1, y1, x2, y2), radius=radius, fill=fill, outline=outline, width=stroke)

    padding_x = int(item.get("padding_x", 18))
    padding_y = int(item.get("padding_y", 12))
    max_size = int(item.get("max_font_size", 36))
    min_size = int(item.get("min_font_size", 20))
    font_path = bold_font if item.get("bold") else dialogue_font
    font, lines, leading = fit_text(
        draw,
        item["text"],
        (x2 - x1) - padding_x * 2,
        (y2 - y1) - padding_y * 2,
        font_path,
        max_size,
        min_size,
    )
    total_height = lines_height(draw, lines, font, leading)
    y = y1 + ((y2 - y1) - total_height) / 2
    color = tuple(item.get("color", [18, 18, 18, 255]))
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font)
        line_width = box[2] - box[0]
        line_height = box[3] - box[1]
        x = x1 + ((x2 - x1) - line_width) / 2 - box[0]
        draw.text((x, y - box[1]), line, font=font, fill=color)
        y += line_height + leading


def draw_masthead(
    image: Image.Image,
    draw: ImageDraw.ImageDraw,
    image_size: tuple[int, int],
    spec: dict,
    title_font_path: str,
) -> None:
    if not spec.get("title"):
        return

    width, height = image_size
    masthead = spec.get("masthead", {})
    x1, y1, x2, y2 = scaled_box(masthead.get("box", [34, 20, 380, 112]), width, height)
    style = masthead.get("style", "code-plaque")

    ink = tuple(masthead.get("ink", [18, 30, 42, 255]))
    blue = tuple(masthead.get("accent", [33, 117, 155, 255]))
    coral = tuple(masthead.get("secondary_accent", [226, 102, 71, 255]))
    cream = tuple(masthead.get("fill", [255, 253, 247, 240]))

    if style == "image":
        image_path = masthead.get("image_path")
        if not image_path:
            raise ValueError("masthead.style='image' requires masthead.image_path")
        logo_path = resolve_skill_path(image_path)
        logo = Image.open(logo_path).convert("RGBA")
        box_width = x2 - x1
        box_height = y2 - y1
        scale = min(box_width / logo.width, box_height / logo.height)
        new_size = (max(1, round(logo.width * scale)), max(1, round(logo.height * scale)))
        logo = logo.resize(new_size, Image.Resampling.LANCZOS)
        anchor = masthead.get("anchor", "left")
        if anchor == "center":
            px = x1 + (box_width - logo.width) // 2
        elif anchor == "right":
            px = x2 - logo.width
        else:
            px = x1
        py = y1 + (box_height - logo.height) // 2
        image.alpha_composite(logo, (px, py))
        if spec.get("episode_title"):
            subtitle_font = load_font(masthead.get("subtitle_font", DEFAULT_FALLBACK_FONT), int(masthead.get("subtitle_size", 22)))
            subtitle_pos = masthead.get("episode_position", [px, py + logo.height + 4])
            sx, sy = scaled_box(subtitle_pos, width, height)
            draw.text((sx, sy), spec["episode_title"], font=subtitle_font, fill=tuple(masthead.get("subtitle_color", [60, 64, 68, 255])))
    elif style == "code-wordmark":
        badge_x = x1
        badge_y = y1 + 15
        draw.rounded_rectangle((badge_x, badge_y, badge_x + 30, badge_y + 30), radius=7, fill=blue)
        badge_font = load_font(DEFAULT_FALLBACK_FONT, 25)
        draw.text((badge_x + 7, badge_y - 4), "<", font=badge_font, fill=(255, 255, 255, 255))

        title_font = load_font(title_font_path, int(masthead.get("title_size", 46)))
        x = badge_x + 42
        y = y1 + 4
        title = spec["title"]
        parts = [("the_", ink), ("loop", blue), ("()", coral)] if title == "the_loop()" else [(title, ink)]
        for text, color in parts:
            draw.text((x, y), text, font=title_font, fill=color)
            x += text_width(draw, text, title_font)
        draw.line((badge_x + 42, y1 + 58, x - 6, y1 + 58), fill=blue, width=4)

        if spec.get("episode_title"):
            subtitle_font = load_font(masthead.get("subtitle_font", DEFAULT_FALLBACK_FONT), int(masthead.get("subtitle_size", 22)))
            draw.text((badge_x + 42, y1 + 63), spec["episode_title"], font=subtitle_font, fill=tuple(masthead.get("subtitle_color", [60, 64, 68, 255])))
    elif style == "code-plaque":
        draw.rounded_rectangle((x1 + 6, y1 + 7, x2 + 6, y2 + 7), radius=18, fill=(18, 30, 42, 55))
        draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill=cream, outline=blue, width=4)
        badge_x = x1 + 18
        badge_y = y1 + 18
        draw.rounded_rectangle((badge_x, badge_y, badge_x + 31, badge_y + 31), radius=7, fill=blue)
        badge_font = load_font(DEFAULT_FALLBACK_FONT, 25)
        draw.text((badge_x + 7, badge_y - 4), "<", font=badge_font, fill=(255, 255, 255, 255))

        title_font = load_font(title_font_path, int(masthead.get("title_size", 42)))
        x = badge_x + 42
        y = y1 + 10
        title = spec["title"]
        parts = [("the_", ink), ("loop", blue), ("()", coral)] if title == "the_loop()" else [(title, ink)]
        for text, color in parts:
            draw.text((x, y), text, font=title_font, fill=color)
            x += text_width(draw, text, title_font)

        if spec.get("episode_title"):
            subtitle_font = load_font(masthead.get("subtitle_font", DEFAULT_FALLBACK_FONT), int(masthead.get("subtitle_size", 23)))
            draw.text((x1 + 24, y2 - 33), spec["episode_title"], font=subtitle_font, fill=tuple(masthead.get("subtitle_color", [60, 64, 68, 255])))
    else:
        font = load_font(title_font_path, int(masthead.get("title_size", 44)))
        draw.text((x1, y1), spec["title"], font=font, fill=ink)

    if spec.get("issue"):
        issue_font = load_font(masthead.get("issue_font", DEFAULT_FALLBACK_FONT), int(masthead.get("issue_size", 24)))
        ix, iy = scaled_box(masthead.get("issue_position", [width - 130, 30]), width, height)
        draw.text((ix, iy), spec["issue"], font=issue_font, fill=tuple(masthead.get("issue_color", [70, 70, 70, 255])))


def main() -> None:
    parser = argparse.ArgumentParser(description="Letter a comic strip with masthead and speech balloons.")
    parser.add_argument("--input", required=True, help="Unlettered comic art PNG/JPG")
    parser.add_argument("--output", required=True, help="Lettered output PNG/JPG")
    parser.add_argument("--spec", required=True, help="JSON lettering spec")
    parser.add_argument("--dialogue-font", default=DEFAULT_DIALOGUE_FONT)
    parser.add_argument("--bold-font", default=DEFAULT_DIALOGUE_FONT)
    parser.add_argument("--title-font", default=DEFAULT_TITLE_FONT)
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    image = Image.open(args.input).convert("RGBA")
    draw = ImageDraw.Draw(image)

    draw_masthead(image, draw, image.size, spec, args.title_font)
    for item in spec.get("balloons", []):
        draw_balloon(draw, image.size, item, args.dialogue_font, args.bold_font)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(out, quality=int(spec.get("quality", 96)))


if __name__ == "__main__":
    main()
