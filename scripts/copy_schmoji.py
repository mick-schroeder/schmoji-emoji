# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Mick Schroeder, LLC.
# #!/usr/bin/env python3
import argparse
from pathlib import Path
import shutil
import sys
from typing import Iterable

# Default set built from Mick's Swift arrays (upper-case hex).
_SWIFT_CODES = [
    # blue
    "1F40B", "1F456", "1F48E", "1F699", "1F6F8", "1F976", "1F9CA", "1F41F", "1FA72", "26F8",
    # brown
    "1F954",
    # green
    "1F340", "1F36C", "1F40D", "1F422", "1F438", "1F966", "1F96C", "1F996", "1F432", "1F951",
    # orange
    "1F34A", "1F357", "1F415", "1F431", "1F436", "1F439", "1F955", "1F981", "1F9F6", "1F621",
    # pink
    "1F338", "1F351", "1F437", "1F498", "1F9A9", "1F9C1", "1F9E0", "1F9FC", "1FA79", "1FA81",
    # purple
    "1F346", "1F347", "1F45A", "1F45B", "1F47E", "1F52E", "1F9AA", "1FA71", "1F97C", "1F43C",
    # red
    "1F336", "1F34E", "1F353", "1F3B8", "1F444", "1F479", "1F680", "1F681", "1F969", "1F980",
    # yellow
    "1F34C", "1F355", "1F44C", "1F4A1", "1F4AA", "1F603", "1F60E", "1F618", "1F602", "1F92F",
]

DEFAULT_STYLES = ["Color", "3D"]  # sensible default for game assets; override with --styles


def parse_styles(arg: str | None) -> list[str]:
    if not arg:
        return DEFAULT_STYLES
    parts = [p.strip() for p in arg.split(",") if p.strip()]
    if not parts:
        return DEFAULT_STYLES
    return parts


def normalize_codes(codes: Iterable[str]) -> list[str]:
    out = []
    seen = set()
    for c in codes:
        cc = c.strip().lower()
        if not cc:
            continue
        if cc not in seen:
            seen.add(cc)
            out.append(cc)
    return out


def copy_matches(unicode_root: Path, out_root: Path, styles: list[str], codes: list[str], dry_run: bool) -> None:
    any_missing = False
    for style in styles:
        src_style_dir = unicode_root / style
        if not src_style_dir.exists():
            print(f"⚠️  Missing style folder in unicode: {src_style_dir}")
            any_missing = True
            continue
        dst_style_dir = out_root / style
        if not dry_run:
            dst_style_dir.mkdir(parents=True, exist_ok=True)
        for code in codes:
            # Match base code (e.g., 26f8.svg) and variants with extra suffixes (e.g., 26f8 fe0f.png)
            candidates = sorted(src_style_dir.glob(f"{code}*.*"))
            if not candidates:
                print(f"⚠️  Not found: {src_style_dir}/{code}.*")
                any_missing = True
                continue

            # Pick one preferred source: exact match > FE0F variant > first candidate
            preferred = None
            for pat in (f"{code}.*", f"{code} fe0f.*"):
                found = sorted(src_style_dir.glob(pat))
                if found:
                    preferred = found[0]
                    break
            if preferred is None:
                preferred = candidates[0]

            # Normalize destination filename to `<code><ext>` so re-runs overwrite (no `_2` growth)
            dst = dst_style_dir / f"{code}{preferred.suffix}"

            if dry_run:
                # Show removals and copy
                for old in sorted(dst_style_dir.glob(f"{code}*.*")):
                    print(f"DRY-RUN: remove {old}")
                print(f"DRY-RUN: copy {preferred} -> {dst}")
            else:
                # Remove existing files for this code to avoid duplicates from prior runs
                for old in sorted(dst_style_dir.glob(f"{code}*.*")):
                    try:
                        old.unlink()
                    except Exception as e:
                        print(f"⚠️  Could not remove {old}: {e}")
                shutil.copy2(preferred, dst)
                print(f"copy {preferred} -> {dst}")
    if any_missing:
        print("\n⚠️  Some assets were missing. Consider regenerating the unicode folder first.")


def main():
    p = argparse.ArgumentParser(
        description=(
            "Copy a curated set of emoji assets from the flat 'unicode' folders into a top-level 'schmoji' folder.\n"
            "By default copies styles: " + ", ".join(DEFAULT_STYLES) + "."
        )
    )
    p.add_argument(
        "--unicode-root",
        default=None,
        help=(
            "Path to the 'unicode' root produced by rename_files.py (default: ../unicode if root is assets, or repoRoot/unicode)."
        ),
    )
    p.add_argument(
        "--out",
        default=None,
        help=("Destination root for schmoji (default: repoRoot/schmoji)."),
    )
    p.add_argument(
        "--styles",
        default=None,
        help=("Comma-separated list of styles to copy (e.g., 'Color,Flat,High Contrast,3D'). Default: '" + ", ".join(DEFAULT_STYLES) + "'."),
    )
    p.add_argument(
        "--codes",
        default=None,
        help=(
            "Optional comma-separated list of Unicode hex codes to copy (e.g., '1F954,1F340'). "
            "If omitted, uses the built-in set from Swift."
        ),
    )
    p.add_argument("root", nargs="?", default=".", help="Repo root or assets folder (default: .)")
    p.add_argument("--dry-run", "-n", action="store_true", help="Show what would happen.")

    args = p.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"❌ Path not found: {root}")
        sys.exit(1)

    # Determine repo root (we want top-level unicode/schmoji beside assets)
    if (root / "assets").exists():
        repo_root = root
    elif (root.name == "assets") and root.parent.exists():
        repo_root = root.parent
    else:
        # Fallback: climb until we see assets or stop at root
        rr = root
        while rr.parent != rr and not (rr / "assets").exists():
            rr = rr.parent
        repo_root = rr

    unicode_root = Path(args.unicode_root).resolve() if args.unicode_root else (repo_root / "unicode").resolve()
    out_root = Path(args.out).resolve() if args.out else (repo_root / "schmoji").resolve()

    styles = parse_styles(args.styles)

    if args.codes:
        codes = normalize_codes([c for c in args.codes.split(",")])
    else:
        codes = normalize_codes(_SWIFT_CODES)

    if not unicode_root.exists():
        print(f"❌ Unicode root not found: {unicode_root}\nRun rename_files.py first to populate it.")
        sys.exit(1)

    print(f"Using unicode root: {unicode_root}")
    print(f"Writing to: {out_root}")
    print(f"Styles: {styles}")
    print(f"Codes: {len(codes)} entries")

    copy_matches(unicode_root, out_root, styles, codes, args.dry_run)


if __name__ == "__main__":
    main()

# Note: After creating this file, run `chmod +x scripts/copy_schmoji.py` to make it executable.