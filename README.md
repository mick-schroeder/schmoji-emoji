# Mick Schroeder's Schmoji Emoji

*A fork and tooling around Microsoft’s Fluent Emoji, tailored for Mick Schroeder’s projects.*

> **What is this?**
> Schmoji Emoji is a curated, game‑ready subset of Fluent Emoji plus scripts that:
> 1) flatten filenames to Unicode (e.g., `potato_color.svg` → `1f954.svg`),
> 2) prefer **Default** skintone variants when present, and
> 3) copy a selected set into a `schmoji/` folder for use in apps/games.

## Quick start

From the repo root:

```bash
# 1) Build the flat Unicode asset set (writes to ./unicode)
python3 scripts/rename_files.py

# 2) Copy your game’s subset (writes to ./schmoji)
python3 scripts/copy_schmoji.py
```

### Using Makefile

You can also use the included **Makefile** for convenience:

```bash
# Run both scripts (build unicode + schmoji)
make

# Or run them individually
make unicode
make schmoji

# Clean up generated folders
make clean
```

This is equivalent to manually running the two Python commands above.

**Notes**
- Run with `--dry-run` to preview actions.
- Only the **Default** skintone assets are copied when skintone variants exist.
- `copy_schmoji.py` defaults to styles `Color` and `3D` and the code list used in the game; override with `--styles` or `--codes`.

## Folder layout (after running scripts)

```
assets/                 # upstream Fluent Emoji assets (from Microsoft)
unicode/                # flat, Unicode‑named assets by style (generated)
  ├─ Color/
  ├─ Flat/
  ├─ High Contrast/
  └─ 3D/
schmoji/                # curated subset for the game (generated)
  ├─ Color/
  └─ 3D/
scripts/
  ├─ rename_files.py    # flatten/copy into ./unicode (Default skintone only)
  └─ copy_schmoji.py    # copy selected codes into ./schmoji
```

## Attribution

This project is a fork of **[Microsoft Fluent Emoji](https://github.com/microsoft/fluentui-emoji)**. Emoji artwork remains © Microsoft and is used under the terms of the upstream project’s license. This fork adds scripts and a curated build process for app/game use.

## Contact

Spotted an issue or want a new variant supported? Please **[open an issue](../../issues/new)**.