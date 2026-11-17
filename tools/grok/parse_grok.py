"""Read-only extraction of the GROK mirror site's generated command pages into JSONL.

Usage: python3 tools/grok/parse_grok.py <extracted-site-dir> [out.jsonl]
  <extracted-site-dir> = directory created by `tar -xJf raw/grok/commandlinefu-mirror-site.tar.xz`
  (it contains public/commands/view/<id>/index.html).

Never executes archived code. AI-written descriptions and "derived" (inferred) tags on the pages are
deliberately NOT extracted: they are not original commandlinefu.com data.
"""
import html, json, os, re, sys

site = sys.argv[1]
ROOT = os.path.join(site, 'public', 'commands', 'view')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', '..', 'raw', 'grok', 'grok_commands.jsonl')

def g(pat, s, flags=re.S):
    m = re.search(pat, s, flags)
    return m.group(1) if m else None

def text(frag):
    if frag is None:
        return None
    frag = re.sub(r'<br\s*/?>', '\n', frag)
    frag = re.sub(r'</p>\s*<p>', '\n\n', frag)
    return html.unescape(re.sub(r'<[^>]+>', '', frag)).strip()

rows, bad = [], []
for d in sorted(os.listdir(ROOT), key=lambda x: int(x) if x.isdigit() else -1):
    p = os.path.join(ROOT, d, 'index.html')
    if not d.isdigit() or not os.path.exists(p):
        continue
    s = open(p, encoding='utf-8').read()
    main = g(r'<main class="wrap">(.*?)</main>', s)
    if not main:
        bad.append(d); continue
    meta = g(r'<div class="meta-bar">(.*?)</div>', main) or ''
    plain = [text(v) for c, v in re.findall(r'<span(?: class="([^"]*)")?>(.*?)</span>', meta, re.S) if not c]
    votes = g(r'<span class="votes">(-?\d+) votes?</span>', meta)
    links = re.findall(r'<p class="links"[^>]*>(.*?)</p>', main, re.S)
    hrefs = re.findall(r'href="([^"]+)"', links[0]) if links else []
    rows.append(dict(
        id=int(d), title=text(g(r'<h1>(.*?)</h1>', main)),
        votes=int(votes) if votes else None,
        author=next((x[3:] for x in plain if x.startswith('by ')), None),
        date=next((x for x in plain if re.match(r'\d{4}-\d\d-\d\d', x)), None),
        source=text(g(r'<span class="pill">(.*?)</span>', meta)),
        code=text(g(r'<pre class="code"><code>(.*?)</code></pre>', main)),
        desc=text(g(r'<div class="desc">(.*?)</div>', main)),
        tags=[html.unescape(t) for t in re.findall(r'<a class="tag tag-original" href="/commands/tagged/([^/"]+)/"', main)],
        original_url=hrefs[0] if hrefs else None, wayback_url=hrefs[1] if len(hrefs) > 1 else None,
    ))

with open(OUT, 'w', encoding='utf-8') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
print('parsed', len(rows), 'bad', len(bad), bad[:10])
