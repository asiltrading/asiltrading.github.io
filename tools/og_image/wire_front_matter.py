#!/usr/bin/env python3
"""
Add `image: /assets/img/og/<slug>.png` to each part's front matter so that
jekyll-seo-tag emits a per-part og:image. Idempotent: skips files that
already declare an `image:` field.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTS_DIR = ROOT / "_parts"


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return False
    end = text.find("\n---", 4)
    if end == -1:
        return False
    fm = text[4:end]
    if any(line.strip().startswith("image:") for line in fm.splitlines()):
        return False
    slug = path.stem
    new_fm = fm.rstrip() + f'\nimage: "/assets/img/og/{slug}.png"\n'
    new_text = "---\n" + new_fm + text[end:]
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> None:
    changed = 0
    for p in sorted(PARTS_DIR.glob("*.md")):
        if patch(p):
            changed += 1
            print(f"  patched {p.relative_to(ROOT)}")
    print(f"\nDone. patched={changed}")


if __name__ == "__main__":
    main()
