# Themelet Quality Checklist

Use this checklist when planning, reviewing, or packaging a WordPress themelet.

## Fit

- The site is mostly static and intentionally narrow in scope.
- The user wants WordPress hosting, activation, plugin hooks, or deployment, not a full CMS editing workflow.
- A normal theme or block theme would be heavier than the job requires.

## WordPress Contract

- `style.css` has valid theme headers: theme name, description, version, text domain, requirements, author, and license.
- `functions.php` exits when `ABSPATH` is missing.
- Assets are enqueued with `wp_enqueue_style()` and `wp_enqueue_script()` where appropriate.
- `index.php` includes `language_attributes()`, `bloginfo( 'charset' )`, viewport meta, `wp_head()`, `body_class()`, and `wp_footer()`.
- Helper functions and constants use a unique project prefix.
- No starter names remain in function names, handles, text domains, visible copy, or file comments.

## Static-Site Integrity

- The original HTML/CSS mental model is still clear.
- Static content was not moved into unnecessary database settings.
- Asset paths are local, portable, and resolved through a helper.
- External dependencies are intentional and documented in code only when the dependency is non-obvious.

## Front-End Polish

- Layout works at mobile, tablet, and desktop widths.
- The first viewport shows the actual subject of the site.
- Images have useful `alt` text or empty `alt` when decorative.
- Focus states are visible.
- Text does not overlap or overflow buttons, cards, nav, or hero areas.
- The design does not read as an accidental one-color palette unless the source brand requires it.

## Packaging

- `screenshot.png` exists and represents the installed front page.
- ZIP archive contains one top-level folder with the theme files inside it.
- Development-only files, source maps, `.git`, `node_modules`, and temporary exports are excluded unless explicitly needed.
- PHP syntax checks pass.
- The theme activates in WordPress without fatal errors.
