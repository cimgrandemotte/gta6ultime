#!/usr/bin/env python3
"""Fail if any local image source is rendered more than once across HTML pages."""
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

class Images(HTMLParser):
    def __init__(self, page: Path):
        super().__init__()
        self.page = page
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() != "img":
            return
        src = dict(attrs).get("src", "").strip()
        if src and not src.startswith(("http://", "https://", "data:")):
            self.sources.append((self.page.parent / src.split("#", 1)[0].split("?", 1)[0]).resolve())

def main() -> int:
    uses = defaultdict(list)
    for page in ROOT.rglob("*.html"):
        parser = Images(page)
        parser.feed(page.read_text(encoding="utf-8", errors="replace"))
        for image in parser.sources:
            uses[image].append(page.relative_to(ROOT))
    duplicates = {path: pages for path, pages in uses.items() if len(pages) > 1}
    missing = [path for path in uses if not path.is_file()]
    non_jpg = [path for path in uses if path.suffix.lower() not in {".jpg", ".jpeg"}]
    if duplicates:
        for path, pages in duplicates.items():
            print("DUPLICATE:", path, "=>", ", ".join(map(str, pages)))
    if missing:
        for path in missing:
            print("MISSING:", path)
    if non_jpg:
        for path in non_jpg:
            print("NON-JPG:", path)
    if duplicates or missing or non_jpg:
        return 1
    print(f"OK: {len(uses)} unique local images, all exist and are JPEG.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
