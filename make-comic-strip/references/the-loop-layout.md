# the_loop() Daily Strip Layout

Use this as the default production layout for finished `the_loop()` comic strips.

## Canvas

- Export size: `2172 x 724`.
- Structure: four equal landscape panels in one horizontal row.
- Use clean panel borders and enough upper whitespace for balloons.
- Keep the generated art free of readable text; add all lettering afterward.
- Panel 1 must reserve the upper-left masthead area before art generation.

## Masthead

Use the transparent approved logo in the first panel only:

```json
{
  "title": "the_loop()",
  "episode_title": "Episode Title",
  "issue": "#000",
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
    "subtitle_color": [24, 30, 36, 255],
    "issue_font": "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
    "issue_color": [58, 64, 70, 255]
  }
}
```

Do not place the logo in the last panel by default. If a user asks for a special sign-off variant, keep it small, transparent, and away from speech balloons, characters, props, laptop screens, and table edges.

## Balloon Defaults

- Use `/System/Library/Fonts/Supplemental/Arial Bold.ttf` for crisp dialogue.
- Use fully opaque white rounded rectangles with strong black outlines.
- Start dialogue around 30-34px for typical balloons.
- Manually line-break important balloons.
- Put balloons in the upper third when possible, but keep panel 1 clear of the masthead.

## QA

- The masthead reads cleanly at chat-preview size.
- The episode title and issue sit to the right of the logo, not under it.
- The title block feels like built-in strip furniture, not a sticker.
- No balloon or tail touches the logo, episode title, or issue number.
- No second logo appears unless the user requested that variant.
