# Comic Lettering Reference

## Text Hierarchy

Use three levels:

- Masthead: branded, compact, visually distinct from speech balloons.
- Dialogue: largest and highest contrast; readable at preview size.
- Metadata: issue number, episode title, or date; small and unobtrusive.

For a 2000-2400px wide strip, dialogue usually needs 28-40px type depending on font and balloon size. If preview readability matters, choose larger text and fewer words. The dialogue must be legible in the Codex/chat preview, not merely at original size.

## Font Choices

Prefer installed rounded fonts with clean counters and strong shapes. Good local defaults on macOS:

- Primary dialogue: `/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf`
- Alternate dialogue only for a looser hand-lettered feel: `/System/Library/Fonts/Supplemental/ChalkboardSE.ttc`
- Fallback dialogue: `/System/Library/Fonts/Supplemental/Comic Sans MS Bold.ttf`
- Masthead: `/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf`

If a dedicated comic lettering font is available in the project, use it for dialogue. Avoid thin, condensed, script, or overly novelty fonts for balloons.

## Balloon Placement

Place balloons in the upper third when the art leaves room there. Keep tails short and angled toward the mouth or face, not the body. Avoid tails crossing another balloon, a face, or the key prop.

In two-speaker panels, left character's balloon should usually sit left of right character's balloon. The reader should never have to guess which balloon comes first.

Use rounded rectangles for a clean production baseline. Use cloud, jagged, or wavy balloons only when the balloon shape itself is part of the joke or emotion.

## Line Breaks

Use manual line breaks in the spec or the lettering script's wrapping to create compact phrase groups:

- Good: `The internet / needed closure.`
- Weak: `The internet needed / closure.`

Aim for balanced lines. Avoid one very short orphan word unless it is the punchline.

For final polish, manually line-break every important balloon. Do not trust auto-wrap for the final export.

## Dialogue Length

As a default, keep each panel under 10-14 total dialogue words, and keep each balloon to one clear thought. If a panel needs more, simplify the joke before shrinking type. The drawing should carry part of the setup.

Use direct wording first, then wit. A good `the_loop()` balloon should read instantly:

- Good: `I found the / final draft.`
- Good: `They all / say final.`
- Good: `Thirteen.`
- Weak: `Those are stages / of certainty.`

The final panel should be brief enough to land like a beat, not an explanation.

## Title Design

The masthead should not look like a speech balloon. Use a colored outline, badge, tab, or code-like wordmark. For `the_loop()`, code-flavored styling is appropriate: blue accent, rounded technical feel, and small punctuation/cursor motifs. Prefer the `code-wordmark` masthead when the title sits inside a panel; use `code-plaque` only when it has enough space away from dialogue.

For final `the_loop()` strips, prefer the approved raster masthead asset with `masthead.style: "image"` and `image_path: "assets/the-loop-logo.png"`. The lettering script resolves this path relative to the skill folder. Keep it clear of speech balloons and scale it large enough that the underscore and parentheses remain readable.

Reserve a title safe area in the first panel. The masthead image box, episode title, and issue marker must not touch or overlap speech balloons. The lettering script enforces this by default and accepts an explicit `masthead.safe_area` override when a custom title layout needs a different protected rectangle.

For standard `the_loop()` desk scenes, split the title system: keep the `the_loop()` logo at the top of the first panel, and place only the episode/comic name plus issue number in the brown desk/table band at the bottom. On a `2172 x 724` strip, start with `box: [32, 16, 285, 108]`, `episode_position: [305, 653]`, `subtitle_size: 14-18`, `issue_position: [305, 678]`, and `safe_padding: 8`. This preserves the branded masthead while keeping the episode title out of the speech-balloon area.

## Clarity QA

Before final delivery, inspect the rendered PNG and ask:

- Can the premise be understood by panel 2?
- Does each balloon contain one clear thought?
- Are all important line breaks intentional?
- Is every balloon visually centered?
- Is the title safe area clear of every balloon and tail?
- Are tails pointing to the correct speaker without crossing other tails?
- Is the punchline shorter than the setup?
- Would the text still read after the image is scaled down in chat?

If any answer is no, rewrite the text or reposition balloons and export again.

## Generated Art Rules

Prompt image models for blank balloons or no balloons, blank screens, and abstract UI blocks. Add all readable text afterward. If the generated art includes incorrect text or backwards screen text, regenerate or cover it before lettering.

For laptop scenes, specify: "the screen is on the inside of the open laptop and faces the user; if viewed from behind, show only the plain back of the display." Make this explicit in every laptop prompt: the outside back lid is plain dark gray or neutral, with no UI blocks, browser chrome, buttons, glow, page layouts, check marks, or screen content. If the viewer is looking at the opposite side from Paige/Dash, the visible laptop surface must be the plain back lid.
