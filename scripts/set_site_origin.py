#!/usr/bin/env python3
"""Set absolute SEO URLs once the production origin/path is known.

Examples:
  python3 scripts/set_site_origin.py https://guide.example.fr --apply
  python3 scripts/set_site_origin.py https://owner.github.io/repo --apply

The script intentionally requires --apply before changing any file.
"""
from __future__ import annotations
import argparse, re
from pathlib import Path
from urllib.parse import urlsplit, urljoin

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER = 'https://gta6-ultimate-guide.example.com'
ATTR = re.compile(r'''\b([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')''')

def attr(tag: str, key: str) -> str | None:
    for match in ATTR.finditer(tag):
        if match.group(1).lower() == key.lower():
            return match.group(2) if match.group(2) is not None else match.group(3)
    return None

def normalize_origin(value: str) -> str:
    p = urlsplit(value)
    if p.scheme != 'https' or not p.netloc or p.query or p.fragment:
        raise ValueError('Use an HTTPS origin/path, e.g. https://guide.example.fr or https://owner.github.io/repo')
    if p.hostname and (p.hostname == 'example.com' or p.hostname.endswith(('.example.com', '.example.org', '.example.net', '.invalid', '.test', '.localhost'))):
        raise ValueError('Reserved placeholder/test domains cannot be used as the public site origin.')
    return value.rstrip('/')

def path_from_file(path: Path) -> str:
    return '/' + path.relative_to(ROOT).as_posix()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('origin', help='HTTPS production origin; GitHub Pages project paths are allowed')
    ap.add_argument('--apply', action='store_true', help='write changes; otherwise show a dry-run summary')
    args = ap.parse_args()
    origin = normalize_origin(args.origin)
    html_files = [ROOT/'index.html', *sorted((ROOT/'pages').rglob('*.html'))]
    root_text=(ROOT/'index.html').read_text(encoding='utf-8')
    root_link=re.search(r'<link\b[^>]*>',root_text,re.I)
    root_url=attr(root_link.group(0),'href') if root_link and (attr(root_link.group(0),'rel') or '').lower()=='canonical' else None
    old_path=urlsplit(root_url).path if root_url else '/index.html'
    old_prefix=old_path[:-len('/index.html')] if old_path.endswith('/index.html') else ''
    changes=[]
    for f in html_files:
        text=f.read_text(encoding='utf-8')
        canonical=f'{origin}{path_from_file(f)}'
        found_canonical=False
        def canonical_tag(match):
            nonlocal found_canonical
            tag=match.group(0)
            if (attr(tag,'rel') or '').lower() == 'canonical':
                found_canonical=True
                return f'<link rel="canonical" href="{canonical}">'
            return tag
        updated=re.sub(r'<link\b[^>]*>',canonical_tag,text,flags=re.I)
        if not found_canonical:
            print(f'ERROR: canonical missing in {f.relative_to(ROOT)}');return 2
        def metadata_tag(match):
            tag=match.group(0)
            prop=(attr(tag,'property') or '').lower()
            name=(attr(tag,'name') or '').lower()
            content=attr(tag,'content')
            if prop=='og:image' and content and not content.startswith(('https://','http://','data:')):
                absolute=urljoin(origin+path_from_file(f),content)
                return f'<meta property="og:image" content="{absolute}">'
            if prop=='og:url':
                return f'<meta property="og:url" content="{canonical}">'
            return tag
        updated=re.sub(r'<meta\b[^>]*>',metadata_tag,updated,flags=re.I)
        if not re.search(r'<meta\b(?=[^>]*\bproperty=["\']og:url["\'])[^>]*>',updated,re.I):
            updated=updated.replace('</head>',f'<meta property="og:url" content="{canonical}"></head>',1)
        og_image=None
        for match in re.finditer(r'<meta\b[^>]*>',updated,re.I):
            tag=match.group(0)
            if (attr(tag,'property') or '').lower()=='og:image':
                og_image=attr(tag,'content');break
        if og_image and not re.search(r'<meta\b(?=[^>]*\bname=["\']twitter:image["\'])[^>]*>',updated,re.I):
            updated=updated.replace('</head>',f'<meta name="twitter:image" content="{og_image}"></head>',1)
        if updated!=text: changes.append((f,updated))
    sitemap=ROOT/'sitemap.xml'; sm=sitemap.read_text(encoding='utf-8')
    def sitemap_url(match):
        path=urlsplit(match.group(1).strip()).path or '/index.html'
        if old_prefix:
            if path==old_prefix: path='/index.html'
            elif path.startswith(old_prefix+'/'): path=path[len(old_prefix):]
        return f'<loc>{origin}{path}</loc>'
    sm=re.sub(r'<loc>\s*(.*?)\s*</loc>',sitemap_url,sm,flags=re.I)
    robots=ROOT/'robots.txt'; rb=robots.read_text(encoding='utf-8')
    rb=re.sub(r'Sitemap:\s*\S+',f'Sitemap: {origin}/sitemap.xml',rb)
    all_files=[(f,t) for f,t in changes]+[(sitemap,sm),(robots,rb)]
    if not args.apply:
        print(f'Dry run: would update canonical/OG metadata in {len(changes)} HTML files, sitemap.xml and robots.txt to {origin}')
        print('Re-run with --apply to write these edits.')
        return 0
    for f,text in all_files: f.write_text(text,encoding='utf-8')
    print(f'Updated {len(changes)} HTML files, sitemap.xml and robots.txt to {origin}')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
