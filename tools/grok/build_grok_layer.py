"""Build the THIRD-PARTY, UNVERIFIED GROK layer in thirdparty/grok/ from raw/grok/grok_commands.jsonl.

Run AFTER tools/process.py (it reads clean/ to decide what the layer may add). It never writes to clean/
or to clean/commandlinefu.sqlite and never executes archived code.

What goes into the layer (only the usable parts):
  commands_gap.jsonl         commands absent from clean/, passing our spam rules (verdict "ok")
  descriptions_original.jsonl original descriptions for clean commands that have none, code identical
  command_tags.csv           tag pairs whose slug is a real, complete tag in our taxonomy and that do not
                             contradict a complete tag block we observed ourselves
  excluded.jsonl             everything rejected above, with the reason
  grok_layer.sqlite          the three usable tables in one database
  layer_stats.json           counts
"""
import collections, csv, hashlib, html, json, os, re, sqlite3

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW, CLEAN, MAN = (os.path.join(ROOT, d) for d in ('raw', 'clean', 'manifests'))
OUT = os.path.join(ROOT, 'thirdparty', 'grok')
os.makedirs(OUT, exist_ok=True)
TARBALL = os.path.join(RAW, 'grok', 'commandlinefu-mirror-site.tar.xz')
SHA = hashlib.sha256(open(TARBALL, 'rb').read()).hexdigest()
PROV = 'grok_mirror_site:sha256=%s (built 2026-11-13 by a third party from an unpublished commands.sqlite; no raw captures)' % SHA
LAYER = 'third_party_unverified'

# reuse the exact spam rules of the verified pipeline
src = open(os.path.join(ROOT, 'tools', 'process.py')).read()
ns = {}
exec('import re,unicodedata\n' + re.search(r'^def norm_ws.*?(?=^# -{5,} HTML)', src, re.S | re.M).group(0), ns)
spam_eval = ns['spam_eval']

ws = lambda s: re.sub(r'\s+', ' ', s or '').strip()
BAD_TITLE = re.compile(r'^Comments \(\d+\)$')
G = {r['id']: r for r in map(json.loads, open(os.path.join(RAW, 'grok', 'grok_commands.jsonl'), encoding='utf-8'))}
O = {r['id']: r for r in map(json.loads, open(os.path.join(CLEAN, 'commands.jsonl'), encoding='utf-8'))}
wb_only = {int(l.split('\t')[0]) for l in open(os.path.join(MAN, 'wayback_only_ids.tsv')) if l.split('\t')[0].isdigit()}

raw_code = {}  # code in our own Wayback view captures, keyed by id
for f in os.listdir(os.path.join(RAW, 'wayback_html', 'views')):
    s = open(os.path.join(RAW, 'wayback_html', 'views', f), encoding='utf-8', errors='replace').read()
    m = re.search(r'<div class="command"[^>]*>(.*?)</div>', s, re.S)
    if m:
        raw_code[int(f.split('_')[0])] = ws(html.unescape(re.sub('<[^>]+>', '', m.group(1))))

stats = collections.Counter()
excluded = []
def exclude(kind, key, reason, **detail):
    stats['excluded_%s_%s' % (kind, reason)] += 1
    excluded.append(dict(kind=kind, key=key, reason=reason, layer=LAYER, provenance=PROV, **detail))

# 1) commands missing from clean/
gap = []
for i in sorted(set(G) - set(O)):
    g = G[i]
    title_ok = not BAD_TITLE.match(g['title'] or '')
    verdict, hits = spam_eval(g['code'], g['title'] if title_ok else None, g['desc'])
    if verdict != 'ok':
        exclude('command', i, 'spam_' + verdict, spam_hits=hits); continue
    if not ws(g['code']):
        exclude('command', i, 'empty_code'); continue
    cv = 'unverified'
    if i in raw_code:
        cv = 'matches_our_raw_capture' if ws(g['code']) == raw_code[i] else 'conflicts_with_our_raw_capture'
        if cv != 'matches_our_raw_capture':
            exclude('command', i, cv); continue
    slug = re.search(r'/commands/view/\d+/([^/?#]+)', g['original_url'] or '')
    gap.append(dict(
        id=i, layer=LAYER, title=g['title'] if title_ok else None,
        title_issue=None if title_ok else 'third_party_title_was_comment_heading(%s);_set_null' % g['title'],
        url_slug=slug.group(1) if slug else None, code=g['code'], description_original=g['desc'],
        author=g['author'], date=g['date'], votes=g['votes'], third_party_source_label=g['source'],
        original_url=g['original_url'], code_check=cv, in_our_wayback_only_list=i in wb_only, provenance=PROV))
stats['gap_commands_usable'] = len(gap)
stats['gap_commands_title_null'] = sum(1 for r in gap if r['title'] is None)
stats['gap_commands_in_wayback_only_list'] = sum(1 for r in gap if r['in_our_wayback_only_list'])
stats['gap_commands_code_matches_our_raw'] = sum(1 for r in gap if r['code_check'] == 'matches_our_raw_capture')

# 2) original descriptions where clean/ has none
descs = []
for i in sorted(set(G) & set(O)):
    if not G[i]['desc'] or ws(O[i].get('description_original')):
        continue
    if ws(G[i]['code']) != ws(O[i]['code']):
        exclude('description', i, 'code_differs_from_clean'); continue
    descs.append(dict(id=i, layer=LAYER, description_original=G[i]['desc'], third_party_source_label=G[i]['source'], provenance=PROV))
stats['descriptions_usable'] = len(descs)

# 3) tag pairs
slug2id = {}
for r in csv.DictReader(open(os.path.join(CLEAN, 'tags.csv'), encoding='utf-8')):
    for s in [r['slug']] + [x for x in r['other_slugs'].split('|') if x]:
        slug2id.setdefault(s, int(r['tag_id']))
ver = collections.defaultdict(set)
for r in csv.DictReader(open(os.path.join(CLEAN, 'command_tags.csv'), encoding='utf-8')):
    ver[int(r['command_id'])].add(int(r['tag_id']))
gap_ids = {r['id'] for r in gap}
pairs = []
for i in sorted(G):
    if i not in O and i not in gap_ids:
        if G[i]['tags']:
            exclude('tag_pairs', i, 'command_not_in_clean_or_layer', n=len(G[i]['tags']))
        continue
    status_ours = O[i].get('tag_status') if i in O else 'unknown'
    for s in dict.fromkeys(G[i]['tags']):
        tid = slug2id.get(s)
        if any(o != s and o.startswith(s) for o in G[i]['tags']) or (len(s) <= 2 and tid is None):
            exclude('tag_pair', '%d:%s' % (i, s), 'truncated_slug'); continue
        if tid is None:
            exclude('tag_pair', '%d:%s' % (i, s), 'slug_not_in_taxonomy'); continue
        if tid in ver[i]:
            st = 'confirmed_by_our_evidence'
        elif status_ours in ('observed_full_block', 'observed_no_tags'):
            exclude('tag_pair', '%d:%s' % (i, s), 'contradicts_our_observed_tag_block', tag_id=tid); continue
        else:
            st = 'unverified_third_party'
        stats['tag_pairs_' + st] += 1
        pairs.append(dict(command_id=i, tag_id=tid, slug=s, status=st, command_in_clean=int(i in O), layer=LAYER))
stats['tag_pairs_usable'] = len(pairs)
stats['tag_pairs_commands'] = len({p['command_id'] for p in pairs})
stats['tag_pairs_commands_in_clean'] = len({p['command_id'] for p in pairs if p['command_in_clean']})
stats['grok_pages_parsed'] = len(G)
stats['grok_tarball_sha256'] = SHA

def jsonl(name, rows):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
jsonl('commands_gap.jsonl', gap)
jsonl('descriptions_original.jsonl', descs)
jsonl('excluded.jsonl', excluded)
with open(os.path.join(OUT, 'command_tags.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['command_id', 'tag_id', 'slug', 'status', 'command_in_clean', 'layer'])
    w.writeheader(); w.writerows(pairs)

db = os.path.join(OUT, 'grok_layer.sqlite')
if os.path.exists(db):
    os.remove(db)
con = sqlite3.connect(db)
con.executescript('''
CREATE TABLE layer_info(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE gap_commands(id INTEGER PRIMARY KEY, title TEXT, title_issue TEXT, url_slug TEXT, code TEXT NOT NULL,
  description_original TEXT, author TEXT, date TEXT, votes INTEGER, third_party_source_label TEXT, original_url TEXT,
  code_check TEXT, in_our_wayback_only_list INTEGER, layer TEXT NOT NULL, provenance TEXT NOT NULL);
CREATE TABLE description_supplement(id INTEGER PRIMARY KEY, description_original TEXT NOT NULL,
  third_party_source_label TEXT, layer TEXT NOT NULL, provenance TEXT NOT NULL);
CREATE TABLE command_tags(command_id INTEGER NOT NULL, tag_id INTEGER NOT NULL, slug TEXT, status TEXT NOT NULL,
  command_in_clean INTEGER, layer TEXT NOT NULL, PRIMARY KEY(command_id, tag_id));
''')
con.executemany('INSERT INTO layer_info VALUES(?,?)', [('layer', LAYER), ('provenance', PROV),
    ('warning', 'Third-party data without raw evidence. Not part of the verified corpus in clean/.')])
con.executemany('INSERT INTO gap_commands VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [(r['id'], r['title'], r['title_issue'], r['url_slug'], r['code'],
    r['description_original'], r['author'], r['date'], r['votes'], r['third_party_source_label'], r['original_url'], r['code_check'],
    int(r['in_our_wayback_only_list']), LAYER, PROV) for r in gap])
con.executemany('INSERT INTO description_supplement VALUES(?,?,?,?,?)', [(r['id'], r['description_original'], r['third_party_source_label'], LAYER, PROV) for r in descs])
con.executemany('INSERT INTO command_tags VALUES(?,?,?,?,?,?)', [(p['command_id'], p['tag_id'], p['slug'], p['status'], p['command_in_clean'], LAYER) for p in pairs])
con.commit()
stats['sqlite_integrity_ok'] = int(con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok')
con.close()

json.dump(dict(sorted(stats.items())), open(os.path.join(OUT, 'layer_stats.json'), 'w'), indent=1)
print(json.dumps(dict(sorted(stats.items())), indent=1))
