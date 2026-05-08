# Regionally Famous Skills

Reusable Codex skills from Regionally Famous.

## Skills

- `build-themelet`: Convert static HTML/CSS sites into tiny installable WordPress themelets.
- `make-comic-strip`: Create and letter readable comic strips with reusable mastheads, speech balloons, and polished typography.

## Layout

Each top-level directory is a standalone skill folder with its own `SKILL.md`, optional `agents/openai.yaml`, references, and assets.

```text
skills/
|-- build-themelet/
|   |-- SKILL.md
|   |-- agents/
|   |-- assets/
|   `-- references/
|-- make-comic-strip/
|   |-- SKILL.md
|   |-- agents/
|   |-- assets/
|   |-- references/
|   `-- scripts/
`-- README.md
```

## Validate

Use Codex's skill validator against an individual skill folder:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py build-themelet
```
