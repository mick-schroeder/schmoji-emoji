# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Mick Schroeder, LLC.
# #!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path

STYLE_DIRS = ["Color", "Flat", "High Contrast", "3D"]
IGNORE_FILES = {".DS_Store"}


def copy_in_style_dir(style_dir: Path, unicode_code: str, out_root: Path, dry_run: bool) -> None:
    """Copy all files from a style directory into a flat output directory named by style.

    Example: assets/Potato/Color/potato_color.svg -> unicode/Color/1f954.svg
    Multiple files for the same style/emoji will get numeric suffixes to avoid collisions.
    """
    if not style_dir.is_dir():
        return

    files = [p for p in sorted(style_dir.iterdir())
             if p.is_file() and p.name not in IGNORE_FILES and not p.name.startswith(".")]

    if not files:
        return

    out_dir = out_root / style_dir.name  # e.g., unicode/Color
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    for src in files:
        ext = src.suffix  # keep original suffix (.svg, .png, etc.)
        target = out_dir / f"{unicode_code}{ext}"
        if dry_run:
            print(f"DRY-RUN: copy (overwrite if exists): {src} -> {target}")
        else:
            shutil.copy2(src, target)  # overwrites if target exists
            print(f"copy: {src} -> {target}")


def process_emoji_dir(emoji_dir: Path, out_root: Path, dry_run: bool) -> None:
    # Skintone handling: If a `Default` variant folder exists, only assets from `Default` are copied; Light/Medium/Dark variants are ignored.
    meta_path = emoji_dir / "metadata.json"
    if not meta_path.exists():
        return

    try:
        with meta_path.open("r", encoding="utf-8") as f:
            meta = json.load(f)
        unicode_code = str(meta.get("unicode", "")).strip().lower()
        if not unicode_code:
            print(f"⚠️  Missing 'unicode' in {meta_path}")
            return
    except Exception as e:
        print(f"⚠️  Failed to read {meta_path}: {e}")
        return

    # Prefer skintone "Default" variant when present; otherwise fall back to root styles
    default_variant = emoji_dir / "Default"
    for style in STYLE_DIRS:
        src_dir = default_variant / style if default_variant.is_dir() else emoji_dir / style
        copy_in_style_dir(src_dir, unicode_code, out_root, dry_run)


def find_repo_root(start: Path) -> Path:
    """Walk up from `start` until we find a directory that contains an `assets` folder;
    if none found, return `start`'s absolute path.
    """
    p = start.resolve()
    while True:
        if (p / "assets").is_dir():
            return p
        if p.parent == p:  # reached filesystem root
            return start.resolve()
        p = p.parent


def resolve_out_root(root: Path, out: str | None) -> Path:
    """Determine where the Unicode flat folders will be written.

    Default: write to `<repo_root>/unicode`, where `repo_root` is the nearest ancestor
    directory containing an `assets` folder. If `root` points at a single emoji folder
    (has metadata.json), we still locate `repo_root` by walking upward.
    """
    if out:
        return Path(out).resolve()

    # Locate the repo root (nearest ancestor with an `assets` folder)
    if (root / "metadata.json").exists():
        repo_root = find_repo_root(root.parent)
    else:
        repo_root = find_repo_root(root)

    return (repo_root / "unicode").resolve()


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Copy Fluent emoji asset files to a flat 'unicode' directory by style, "
            "renaming to their Unicode code (e.g., potato_color.svg -> 1f954.svg)."
        )
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Path to the assets root or an emoji folder (default: current directory).",
    )
    parser.add_argument(
        "--out",
        default=None,
        help=(
            "Output directory root (default: '<repo_root>/unicode', where <repo_root> is the nearest ancestor containing 'assets')."
        ),
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would change without copying.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"❌ Path not found: {root}")
        return

    # Determine the actual assets root: support being run from repo root, assets/, or an emoji folder
    if (root / "assets").is_dir():
        assets_root = root / "assets"
    else:
        assets_root = root

    out_root = resolve_out_root(root, args.out)

    # Ensure output root (and style subfolders) exist even if no files are found
    if not args.dry_run:
        out_root.mkdir(parents=True, exist_ok=True)
        for _style in STYLE_DIRS:
            (out_root / _style).mkdir(parents=True, exist_ok=True)

    # If user points at a single emoji folder, process just that; otherwise walk children under assets_root
    if (assets_root / "metadata.json").exists():
        process_emoji_dir(assets_root, out_root, args.dry_run)
    else:
        for child in sorted(assets_root.iterdir()):
            if child.is_dir():
                process_emoji_dir(child, out_root, args.dry_run)

    if args.dry_run:
        print(f"\n(DRY-RUN) Would write files under: {out_root}")
    else:
        print(f"\nWrote files under: {out_root}")


if __name__ == "__main__":
    main()