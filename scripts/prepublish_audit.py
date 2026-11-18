#!/usr/bin/env python3
"""Dependency-free static prepublication checks for the GTA VI guide."""
from __future__ import annotations
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json, re, sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
class AuditParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.title=0; self.description=0; self.h1=0; self.images=[]; self.refs=[]; self.ids=[]; self.canonicals=[]; self.og_images=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='title': self.title+=1
        if tag=='meta' and d.get('name','').lower()=='description': self.description+=1
        if tag=='h1': self.h1+=1
        if tag=='img': self.images.append(d)
        if tag=='a' and d.get('href'): self.refs.append((d['href'],d.get('target'),d.get('rel','')))
        if tag in ('link','script','img','source'):
            u=d.get('href') or d.get('src')
            if u: self.refs.append((u,None,''))
        if d.get('id'): self.ids.append(d['id'])
        if tag=='link' and 'canonical' in d.get('rel','').lower(): self.canonicals.append(d.get('href',''))
        if tag=='meta' and d.get('property')=='og:image': self.og_images.append(d.get('content',''))

def main():
    errs=[]; warns=[]; placeholder_seen=False; files=[ROOT/'index.html',*sorted((ROOT/'pages').rglob('*.html'))]
    rel_files={p.resolve() for p in ROOT.rglob('*') if p.is_file()}
    page_paths={p.resolve() for p in files}
    for f in files:
        p=AuditParser(); text=f.read_text(encoding='utf-8',errors='replace'); p.feed(text); p.close()
        rel=f.relative_to(ROOT).as_posix()
        if p.title!=1 or p.description!=1 or p.h1!=1: errs.append(f'{rel}: title/description/H1 counts = {p.title}/{p.description}/{p.h1}')
        if len(p.canonicals)!=1: errs.append(f'{rel}: expected exactly one canonical; found {len(p.canonicals)}')
        elif 'gta6-ultimate-guide.example.com' in p.canonicals[0]: placeholder_seen=True
        ids=set(p.ids)
        if len(ids)!=len(p.ids): errs.append(f'{rel}: duplicate id attribute')
        for im in p.images:
            if 'alt' not in im: errs.append(f'{rel}: img missing alt')
            src=im.get('src','')
            if src and not re.search(r'\.(jpe?g)(?:[?#]|$)',src,re.I) and not src.startswith(('https://','http://','data:')):
                errs.append(f'{rel}: local image is not JPG: {src}')
            if '/assets/images/official/' in src or '/assets/images/press/' in src or src.startswith(('assets/images/official/','assets/images/press/')):
                errs.append(f'{rel}: non-generated source image remains; replace with original generated JPG: {src}')
        for href,target,relattr in p.refs:
            u=urlsplit(href)
            if target=='_blank' and 'noopener' not in relattr.split(): warns.append(f'{rel}: target=_blank missing rel=noopener: {href}')
            if u.scheme or href.startswith(('//','data:','mailto:','tel:')): continue
            local=(f.parent/u.path).resolve() if u.path else f.resolve()
            if u.path and not local.exists(): errs.append(f'{rel}: broken local reference {href}')
            if u.fragment and local.suffix=='.html' and local.exists():
                dest=AuditParser(); dest.feed(local.read_text(encoding='utf-8',errors='replace')); dest.close()
                if u.fragment not in dest.ids: errs.append(f'{rel}: fragment target not found: {href}')
        for im in p.og_images:
            if im.startswith('../../') or im.startswith('../') or im.startswith('/'): warns.append(f'{rel}: OG image must be absolute before production: {im}')
    try:
        root=ET.parse(ROOT/'sitemap.xml').getroot(); locs=[e.text for e in root.findall('.//{*}loc')]
        if len(locs)!=len(set(locs)): errs.append('sitemap.xml: duplicate URL')
        root_canonical=AuditParser(); root_canonical.feed((ROOT/'index.html').read_text(encoding='utf-8',errors='replace'))
        canonical_path=urlsplit(root_canonical.canonicals[0]).path if root_canonical.canonicals else '/index.html'
        base_prefix=canonical_path[:-len('/index.html')] if canonical_path.endswith('/index.html') else ''
        listed=set()
        for loc in locs:
            if 'gta6-ultimate-guide.example.com' in (loc or ''): placeholder_seen=True
            path=urlsplit(loc).path
            if base_prefix:
                if path==base_prefix: path='/index.html'
                elif path.startswith(base_prefix+'/'): path=path[len(base_prefix):]
                else: errs.append(f'sitemap URL is outside canonical site path: {loc}')
            relpath=path.lstrip('/')
            listed.add(relpath)
            if relpath and not (ROOT/relpath).exists(): errs.append(f'sitemap URL has no file: {loc}')
        expected={p.relative_to(ROOT).as_posix() for p in files}
        if expected!=listed: errs.append(f'sitemap coverage mismatch: {len(expected-listed)} missing, {len(listed-expected)} extra')
    except Exception as e: errs.append(f'sitemap.xml invalid: {e}')
    try: json.loads((ROOT/'research_data.json').read_text(encoding='utf-8'))
    except Exception as e: errs.append(f'research_data.json invalid: {e}')
    legal_files=[ROOT/'pages/legal/mentions-legales.html',ROOT/'pages/legal/confidentialite.html']
    for legal in legal_files:
        if not legal.exists(): errs.append(f'missing required legal page: {legal.relative_to(ROOT)}'); continue
        if '[[À REMPLIR' in legal.read_text(encoding='utf-8',errors='replace') or '[[À VÉRIFIER' in legal.read_text(encoding='utf-8',errors='replace'):
            errs.append(f'{legal.relative_to(ROOT)}: legal/contact placeholders remain; publication blocked until owner completes them')
    # Search index must only point to existing page paths.
    js=(ROOT/'assets/js/search.js').read_text(encoding='utf-8')
    urls=re.findall(r"url:\s*'([^']+)'",js)
    missing=[u for u in urls if not (ROOT/u).exists()]
    if missing: errs.append('search index targets missing: '+', '.join(missing))
    # Keep all packaged image assets in the requested JPEG format.
    image_files=[p for p in (ROOT/'assets/images').rglob('*') if p.is_file() and p.suffix.lower() not in ('.md',)]
    nonjpg=[p.relative_to(ROOT).as_posix() for p in image_files if p.suffix.lower() not in ('.jpg','.jpeg')]
    if nonjpg: errs.append('non-JPG image assets: '+', '.join(nonjpg))
    bad_jpeg=[]
    for image in image_files:
        try:
            with image.open('rb') as stream:
                if stream.read(3) != b'\xff\xd8\xff': bad_jpeg.append(image.relative_to(ROOT).as_posix())
        except OSError: bad_jpeg.append(image.relative_to(ROOT).as_posix())
    if bad_jpeg: errs.append('image files with non-JPEG content: '+', '.join(bad_jpeg))
    referenced=set()
    for page in files:
        parser=AuditParser(); parser.feed(page.read_text(encoding='utf-8',errors='replace')); parser.close()
        for im in parser.images:
            src=im.get('src','')
            u=urlsplit(src)
            if src and not u.scheme and u.path:
                target=(page.parent/u.path).resolve()
                if target.is_file() and target.suffix.lower() in ('.jpg','.jpeg') and (ROOT/'assets/images').resolve() in target.parents:
                    referenced.add(target)
    unreferenced=[image.relative_to(ROOT).as_posix() for image in image_files if image.resolve() not in referenced]
    if unreferenced: errs.append('unreferenced image assets: '+', '.join(unreferenced))
    if placeholder_seen: errs.append('Production origin is still the reserved placeholder; run scripts/set_site_origin.py with the real HTTPS URL after the owner confirms it.')
    print(f'HTML pages: {len(files)} | local image assets: {len(image_files)} | search targets: {len(urls)}')
    print(f'Errors: {len(errs)} | Warnings: {len(warns)}')
    for e in errs: print('ERROR:',e)
    og_warns=[w for w in warns if 'OG image must be absolute before production' in w]
    for w in warns:
        if w not in og_warns: print('WARN:',w)
    if og_warns: print(f'WARN: {len(og_warns)} relative Open Graph image URLs will be made absolute by the origin configurator.')
    return 1 if errs else 0
if __name__=='__main__': raise SystemExit(main())
