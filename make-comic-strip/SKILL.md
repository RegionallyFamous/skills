---
name: make-comic-strip
description: Create, revise, and production-letter comic strips, including generated comic art, speech balloon placement, mastheads, strip aspect ratios, readable typography, and export-ready PNGs. Use when Codex is asked to make a comic, comic strip, webcomic, recurring character strip, expression sheet, title/masthead, speech balloons, lettering, or to fix comic layout, text readability, aspect ratio, panel flow, or generated-image text problems.
---

# Make Comic Strip

## Overview

Create comics in two passes: generate or assemble clean art first, then add all title, dialogue, captions, and issue text deterministically. Do not rely on image generation for readable lettering unless the user explicitly wants rough concept art.

For `the_loop()` strips, keep the tone pro-WordPress: the joke targets the shared website-building moment, not WordPress or its users. Read `references/the-loop-style.md` before writing or generating `the_loop()` material.

## Workflow

1. Write the strip before making art.
   - Use a four-beat strip rhythm: setup, complication, escalation, turn.
   - Keep dialogue short and explicit enough for large balloons; prefer 1-2 balloons per panel.
   - Use one clear thought per balloon. If a line needs explaining, rewrite it before lettering.
   - Prefer direct joke logic over clever ambiguity: the reader should understand the premise within the first two panels.
   - Put the funniest reversal in the final panel.

2. Generate unlettered art.
   - Use the image-generation skill when bitmap art is needed.
   - Prompt for no readable words, no letters, no numbers, no speech-balloon text, and no screen text.
   - Ask for blank/abstract UI screens; never put the joke on a generated screen.
   - For laptop/computer scenes, explicitly specify which side the screen faces. If the outside back lid faces the viewer, it must be a plain lid with no UI blocks, browser chrome, buttons, glow, page layouts, or screen content.
   - When characters are behind or across from a laptop, the viewer should see only the plain back lid; visible screen UI is allowed only when the viewer is on the same side as the characters.

3. Inspect the art before lettering.
   - Check panel order, character consistency, screen orientation, empty balloon space, and whether the action reads without text.
   - Reject and regenerate any art where UI/content appears on the outside back of a laptop.
   - Regenerate the art before lettering if a physical object is wrong or the panel flow is confusing.

4. Letter deterministically.
   - Prefer `scripts/letter_comic.py` for speech balloons, mastheads, and export PNGs.
   - For `the_loop()`, use the approved masthead asset at `assets/the-loop-logo.png` with `masthead.style: "image"`.
   - For `the_loop()`, place the episode/comic name plus issue number at the top-left of the first panel, and place the `the_loop()` logo at the bottom-left of the last panel.
   - Treat the logo, episode title, and issue number as protected title areas. Do not place speech balloons where they touch or overlap those areas.
   - Use `/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf` for dialogue unless the user asks for a looser hand-lettered look.
   - Use manual line breaks in every important balloon; do not rely on auto-wrapping for final polish.
   - Store the unlettered art and final lettered output together.
   - Keep text large enough to read in the chat preview, not only at full resolution.

5. Render and inspect the final.
   - View the exported PNG at original size and preview size.
   - Fix tails that point to the wrong character, text that feels cramped, or balloons that cover acting.
   - Fix any balloon whose text is not visually centered, instantly readable, or logically clear.
   - If the joke reads muddy, rewrite the dialogue and re-letter before final delivery.

## Lettering Script

Use:

```bash
python3 path/to/make-comic-strip/scripts/letter_comic.py \
  --input unlettered.png \
  --output lettered.png \
  --spec lettering.json
```

The spec file is JSON:

```json
{
  "title": "the_loop()",
  "episode_title": "Cache Me If You Can",
  "issue": "#001",
  "masthead": {
    "style": "image",
    "image_path": "assets/the-loop-logo.png",
    "box": [1660, 646, 1832, 708],
    "episode_position": [56, 42],
    "subtitle_size": 16,
    "issue_position": [56, 70],
    "issue_size": 18,
    "safe_padding": 8
  },
  "balloons": [
    {
      "text": "I found the\nfinal draft.",
      "box": [58, 132, 292, 226],
      "tail": [232, 302],
      "max_font_size": 30,
      "min_font_size": 23
    },
    {
      "text": "Define\nfinal.",
      "box": [320, 132, 476, 212],
      "tail": [402, 260],
      "max_font_size": 31,
      "min_font_size": 24
    }
  ]
}
```

Coordinates are pixels by default. Values between `0` and `1` are treated as normalized fractions of the image size.

## Typography Rules

Read `references/lettering.md` when designing or fixing typography. Core defaults:

- Use deterministic post-lettering for all final comics.
- Use large Arial Rounded Bold lettering, strong black outlines, white balloons, and generous inner padding.
- Keep balloon tails short, avoid crossing faces, and make left-to-right reading order obvious.
- Use a masthead style distinct from speech balloons so the title is not mistaken for dialogue.
- Keep all balloons outside the masthead/title safe area. The lettering script rejects balloon boxes that overlap the masthead, episode title, or issue marker.
- For `the_loop()` desk scenes, put the episode/comic name at top-left of panel 1 and the logo at bottom-left of panel 4.
- If the final is meant for chat/social preview, export at least 2000px wide and make dialogue legible after downscaling.

## Acceptance Checks

- The comic reads left to right without explanation.
- The text is polished: short, direct, manually line-broken, visually centered, and readable at preview size.
- All dialogue is real overlay text, not generated-image text.
- The masthead, issue marker, and episode title are readable but do not steal attention from the gag.
- The title area never overlaps or touches a speech balloon.
- Balloons point to the correct speaker and do not cover important expressions.
- Screens, props, and UI are physically plausible.
- Laptop backs are plain lids; all UI appears only on inner screens that face the characters/viewer correctly.
- The final file and unlettered art are both saved in the project.
