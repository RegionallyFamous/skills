---
name: build-themelet
description: "Create, refine, package, or debug WordPress themelets: tiny classic WordPress themes that wrap mostly static HTML/CSS sites so they install and run on WordPress. Use when the user asks for a themelet, wants GitHub Pages simplicity on WordPress, needs to convert a static site or one-page HTML/CSS design into an installable WordPress theme, or wants WordPress theme headers, enqueued assets, wp_head/wp_footer, asset helpers, screenshots, and ZIP packaging without building a full block theme."
---

# Build Themelet

## Overview

Build "themelets": deliberately small classic WordPress themes that preserve the simplicity of static HTML/CSS while satisfying WordPress theme conventions. A themelet is a static site that learned the WordPress handshake; it should feel closer to GitHub Pages in WordPress clothing than a general-purpose CMS theme.

## Workflow

1. Identify the source: an existing static site, an HTML/CSS mockup, a folder of assets, or a fresh design brief.
2. Confirm the fit. Use a themelet for fixed-purpose sites, microsites, docs fronts, prototypes, campaign pages, product pages, or project homepages. Prefer a normal WordPress theme or block theme when the user needs editable layouts, multiple content templates, WooCommerce, comments, archives, or a durable publishing system.
3. Build or preserve the static experience first. Keep the HTML and CSS readable, local, and direct.
4. Wrap the static page as a classic theme:
   - Put WordPress theme headers in `style.css`.
   - Put setup and enqueue logic in `functions.php`.
   - Put the mostly static page shell in `index.php`.
   - Include `wp_head()`, `wp_footer()`, `language_attributes()`, `bloginfo( 'charset' )`, and `body_class()`.
   - Replace hard-coded local asset URLs with a small asset helper.
5. Start from `assets/themelet-starter/` when useful. Copy it to the target theme slug, then rename the theme headers, text domain, function prefix, constants, enqueue handles, visible copy, and placeholder assets.
6. Keep WordPress integration minimal and intentional. Enqueue CSS and scripts instead of hard-coding them. Add metadata, preload hints, and theme support only when the static site needs them.
7. Verify installability, syntax, asset paths, responsiveness, accessibility basics, and packaging before finishing. Read `references/quality-checklist.md` for review passes.

## Package Shape

Create this minimum structure:

```text
theme-slug/
|-- style.css
|-- functions.php
|-- index.php
|-- site.css
|-- screenshot.png
`-- assets/
    |-- image-or-logo.webp
    `-- another-local-asset.ext
```

Use `screenshot.png` for the WordPress Themes screen whenever the themelet is meant to be shared or installed by someone else.

## Conversion Rules

- Treat `style.css` as the WordPress identity file. Keep actual site styling in `site.css` unless the project already has a different clean split.
- Use a unique PHP prefix based on the slug, such as `acme_themelet_`, and rename every starter function before delivery.
- Use `get_template_directory_uri()` for bundled assets and `get_stylesheet_directory_uri()` only when child-theme behavior is specifically wanted.
- Escape generated URLs and attributes with WordPress helpers such as `esc_url()` and `esc_attr()`.
- Keep static copy in `index.php` unless the user asks for WordPress-managed content. Do not introduce loops, options pages, custom post types, customizer settings, or block templates without a clear reason.
- Preserve plugin compatibility by keeping `wp_head()` and `wp_footer()` in place.
- Prefer local assets for the themelet. External fonts or scripts are acceptable only when the source site already depends on them or the user approves the dependency.
- Make the static page accessible enough to install with confidence: semantic landmarks, a skip link when useful, sensible heading order, alt text, visible focus styles, and responsive layouts.

## What Not To Build

Do not turn a themelet into a full WordPress product by accident. The skill is as much about restraint as scaffolding. Avoid adding:

- Site Editor or `theme.json` systems unless the request is really for a block theme.
- Admin settings pages for copy that can stay static.
- Dynamic menus, widgets, comments, archives, or search unless the user asks for them.
- Page-builder assumptions.
- Database-backed content models for a page that is intentionally fixed.

## Verification

Run these checks from the themelet folder, adapting paths as needed:

```bash
php -l functions.php
php -l index.php
rg -n "TODO|FIXME|themelet_starter|Themelet Starter|themelet-starter" .
rg -n "wp_head|wp_footer|body_class|language_attributes" index.php
```

When a browser or WordPress runtime is available, activate the themelet and inspect the front page, browser console, network panel, mobile viewport, keyboard focus, and WordPress Themes screen.

For ZIP packaging, create an archive with a single top-level theme folder:

```bash
cd ..
zip -r theme-slug.zip theme-slug -x "theme-slug/.git/*" "theme-slug/node_modules/*"
```

## Resources

- `assets/themelet-starter/`: copyable minimal classic themelet starter.
- `references/quality-checklist.md`: review checklist for themelet fit, WordPress integration, polish, and packaging.
