---
name: make-comic-strip
description: Create, revise, and production-letter comic strips, including generated comic art, speech balloon placement, mastheads, strip aspect ratios, readable typography, and export-ready PNGs. Use when Codex is asked to make a comic, comic strip, webcomic, recurring character strip, expression sheet, title/masthead, speech balloons, lettering, or to fix comic layout, text readability, aspect ratio, panel flow, or generated-image text problems.
---

# Make Comic Strip

## Overview

Create comics in two passes: generate or assemble clean art first, then add all title, dialogue, captions, and issue text deterministically. Do not rely on image generation for readable lettering unless the user explicitly wants rough concept art.

For `the_loop()` strips, keep the tone pro-WordPress: the joke targets the shared website-building moment, not WordPress or its users. Read `references/the-loop-style.md` before writing or generating `the_loop()` material.

## the_loop() Production System

For ongoing `the_loop()` work, keep reusable process files in this skill and live series state in the project production folder:

- Project production folder: `/Users/nick/Documents/Projects/WordPress.org/outputs/the_loop/production/`
- Canonical tracker: `episodes.json`
- Series bible: `series-bible.md`
- Easter egg registry: `easter-eggs.json`
- QA checklist: `qa-checklist.md`

Use these helper scripts when making or reviewing batches:

- `scripts/new_episode.py`: creates the next numbered episode folder, appends starter metadata, and writes a strip brief.
- `scripts/migrate_canonical_assets.py`: migrates existing strips to canonical `art`, `lettering`, and `final` filenames while preserving older assets as variants.
- `scripts/lint_episode.py`: validates required fields, status, duplicate issue/slug, canonical filenames, exact dimensions, Paige glasses QA, laptop-screen notes, QA artifacts, defects, and approval state.
- `scripts/build_contact_sheet.py`: creates a batch review sheet from recorded final images.
- `scripts/build_qa_crops.py`: creates all-panel face, laptop, and lettering crop sheets for visual QA.
- `scripts/build_review_packet.py`: creates a batch review packet and moves Codex-checked episodes to `qa_ready`.
- `scripts/promote_variant.py`: promotes a regenerated candidate to canonical assets, archives the previous canonical assets, and resets approval for review.

New `the_loop()` briefs should include one clear WordPress/workflow premise, four panel beats, Paige/Dash continuity rules, no generated readable text, laptop screen orientation instructions, one optional subtle easter egg slot, and the regenerate-first policy for character or object failures.

Codex can mark an episode `qa_ready` after lint and review artifacts pass. Only explicit human approval by Nick can move an episode to `approved` or `published`.

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
   - For `the_loop()`, explicitly prompt Paige Post with rounded dark-rimmed glasses every time she appears; glasses are mandatory character continuity, not optional styling.
   - Ask for blank/abstract UI screens; never put the joke on a generated screen.
   - For laptop/computer scenes, explicitly specify which side the screen faces. If the outside back lid faces the viewer, it must be a plain lid with no UI blocks, browser chrome, buttons, glow, page layouts, or screen content.
   - When characters are behind or across from a laptop, the viewer should see only the plain back lid; visible screen UI is allowed only when the viewer is on the same side as the characters.

3. Inspect the art before lettering.
   - Check panel order, character consistency, screen orientation, empty balloon space, and whether the action reads without text.
   - For Paige Post, reject or repair any appearance without visible rounded dark-rimmed glasses, including side views and tiny background poses.
   - Reject and regenerate any art where UI/content appears on the outside back of a laptop.
   - Regenerate the art before lettering if a physical object is wrong or the panel flow is confusing.
   - Treat bad Paige glasses, face consistency, hands, laptop orientation, or screen logic as blocker defects. Regenerate first; use manual repair only as a recorded exception with before/after QA crops.

4. Letter deterministically.
   - Prefer `scripts/letter_comic.py` for speech balloons, mastheads, and export PNGs.
   - For `the_loop()`, use the approved #011 daily-strip layout in `references/the-loop-layout.md`: one 2172x724 strip, four equal panels, the transparent `assets/the-loop-logo.png` in the top-left of panel 1, and the episode title plus issue number to its right.
   - Reserve real title space like a classic newspaper strip. Do not treat the logo as a floating sticker inside the acting area, and do not place a second logo in the last panel unless the user asks for a special variant.
   - If the logo background is ever not clean, omit the logo from the strip and use the text title until a polished transparent asset exists.
   - Treat the logo, episode title, and issue number as protected title areas. Do not place speech balloons where they touch or overlap those areas.
   - Use `/System/Library/Fonts/Supplemental/Arial Bold.ttf` for dialogue when crisp preview readability matters. Keep Arial Rounded Bold for masthead/episode title unless the user asks for a looser hand-lettered look.
   - Use manual line breaks in every important balloon; do not rely on auto-wrapping for final polish.
   - Treat each balloon tail coordinate as the speaker target, not the literal tail tip. The renderer shortens tails by default so they point toward the mouth/face without stabbing into the character art.
   - Keep balloon boxes on an obvious left-to-right reading path, with tails that do not cross faces, hands, props, title art, or other balloons.
   - Store the unlettered art and final lettered output together.
   - Keep text large enough to read in the chat preview, not only at full resolution.

5. Render and inspect the final.
   - View the exported PNG at original size and preview size.
   - Fix tails that point to the wrong character, text that feels cramped, or balloons that cover acting.
   - Fix any balloon whose text is not visually centered, instantly readable, or logically clear.
   - If the joke reads muddy, rewrite the dialogue and re-letter before final delivery.
   - Build a review packet for batches before approval. Review packets must include a contact sheet, all-panel QA crops, thumbnail preview, lint report, and `qa-review.md`.

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
    "box": [42, 24, 292, 114],
    "anchor": "left",
    "episode_position": [315, 40],
    "subtitle_size": 30,
    "issue_position": [316, 78],
    "issue_size": 21,
    "safe_padding": 12,
    "subtitle_font": "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
    "issue_font": "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"
  },
  "balloons": [
    {
      "text": "I found the\nfinal draft.",
      "box": [58, 132, 292, 226],
      "tail": [232, 302],
      "tail_end_ratio": 0.48,
      "max_tail_length": 130,
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
- Use large Arial Bold dialogue, strong black outlines, fully opaque white balloons, and generous inner padding.
- Keep balloon tails short, point them toward the speaker's mouth/face, avoid crossing faces, and make left-to-right reading order obvious.
- Use a masthead style distinct from speech balloons so the title is not mistaken for dialogue.
- Keep all balloons outside the masthead/title safe area. The lettering script rejects balloon boxes that overlap the masthead, episode title, or issue marker.
- For `the_loop()` desk scenes, use the #011 first-panel masthead layout from `references/the-loop-layout.md`.
- If the final is meant for chat/social preview, export at least 2000px wide and make dialogue legible after downscaling.

## Acceptance Checks

- The comic reads left to right without explanation.
- The text is polished: short, direct, manually line-broken, visually centered, and readable at preview size.
- All dialogue is real overlay text, not generated-image text.
- The masthead, issue marker, and episode title are readable but do not steal attention from the gag.
- `the_loop()` strips use the #011 first-panel masthead layout unless the user asks for a variant.
- The title area never overlaps or touches a speech balloon.
- The logo never appears as an opaque white box over textured art, character art, props, or panel backgrounds.
- Balloons point to the correct speaker and do not cover important expressions.
- Screens, props, and UI are physically plausible.
- Laptop backs are plain lids; all UI appears only on inner screens that face the characters/viewer correctly.
- The final file and unlettered art are both saved in the project.
