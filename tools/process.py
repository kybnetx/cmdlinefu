#!/usr/bin/env python3
"""Re-runnable processing of raw commandlinefu acquisitions -> clean corpus.
Never executes any archived command. Reads only files under raw/.
Usage: python3 tools/process.py   (run from bundle root)
"""
import json, re, os, glob, html, sqlite3, csv, hashlib, collections, unicodedata
import yaml
from bs4 import BeautifulSoup, Comment

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'raw'); CLEAN = os.path.join(ROOT, 'clean'); MAN = os.path.join(ROOT, 'manifests')
os.makedirs(CLEAN, exist_ok=True); os.makedirs(MAN, exist_ok=True)
stats = collections.OrderedDict()
def S(k, n=1): stats[k] = stats.get(k, 0) + n

exclusions = []   # machine-readable quarantine/exclusion log
def EXC(source, key, reason, disposition, detail=None, raw_path=None):
    exclusions.append(dict(source=source, key=str(key), reason=reason, disposition=disposition,
                           detail=detail, raw_path=raw_path))

def norm_ws(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s or '')).strip()

# ---------------- spam rules (conservative) ----------------
STRONG = [r'\breplica\b', r'\brolex\b', r'\bomega\s+(watch|seamaster|speedmaster)', r'\bmoncler\b',
          r'\btiffany\b', r'\blouboutin\b', r'\bwedding\s+(dress|gown)s?\b', r'\bgowns?\b', r'\bugg\s*boots?\b', r'\bviagra\b',
          r'\bcialis\b', r'\bcasino\b', r'\bpayday\s+loans?\b', r'\bhandbags?\b', r'\bjerseys?\b', r'\bnike\s+(air|shoes)\b',
          r'\bcheap\s+\w+\s+(sale|online|outlet)\b', r'\boutlet\s+(store|online|sale)\b', r'\bmichael\s+kors\b', r'\bchanel\b',
          r'\bpandora\b', r'\blouis\s+vuitton\b', r'\bburberry\b', r'\bjewel(le)?ry\b', r'\bsunglasses\b',
          r'\bweight\s+loss\b', r'\bescort\b', r'\bessay\s+writing\b', r'\bseo\s+services?\b',
          r'\bherm[eè]s\b', r'\bjimmy\s+choo\b', r'\btimberland\b', r'\bbreitling\b', r'\bpanerai\b', r'\bcartier\b',
          r'\bpatek\b', r'\bhublot\b', r'\bmont\s?blanc\b', r'\bdress(es)?\b', r'\bmermaid\b', r'\bsweetheart\b',
          r'\btaffeta\b', r'\bbridal\b', r'\bbridesmaid', r'\bprom\b', r'\bklokker\b', r'\bsconto\b', r'\beconomici\b',
          r'\bbarato\b', r'\bvenda\b', r'\boutlet\b', r'\bnuziale\b', r'\bzen\s*cart\b', r'\bugg\b', r'\boakley\b', r'\bray[\s-]?ban\b',
          r'(\$|€|&euro;|£)\s?\d{1,5}[.,]\d{2}\b', r'\b\d{1,5}[.,]\d{2}\s?(€|&euro;|eur|usd)\b']
WEAK = [r'\bcheap\b', r'\bdiscount\b', r'\bbuy\s+\w+\s+online\b', r'\bfree\s+shipping\b', r'\bsale\b', r'\bwatch(es)?\b',
        r'https?://\S+\.(com|net)/\S*(shop|store|buy)']
# Stricter shell-likeness test, applied to the CODE field only.
SHELLISH = re.compile(r'(\|\s*[\w./-]|\$\(|\$\{|\$[A-Za-z_]\w*|\$\d|&&|`|2>&1|>\s*/|>>|<\(|;\s*(do|done|then|fi)\b|'
                      r'(^|[\s(;|])-{1,2}[a-zA-Z][\w-]*(=|\s+[\w./~"\'$-])|'
                      r'(^|[|;&(]\s*)(sudo|grep|e?grep|sed|awk|find|ls|cat|echo|printf|for|while|xargs|curl|wget|ssh|scp|rsync|tar|git|cd|rm|cp|mv|ps|kill|'
                      r'perl|python3?|ruby|apt-get|apt|yum|dnf|dd|mount|umount|chmod|chown|ffmpeg|du|df|netstat|ip|ifconfig|vim?|tail|head|sort|uniq|'
                      r'cut|tr|wc|date|history|alias|export|mkdir|touch|ln|openssl|nc|nmap|lsof|top|watch|screen|tmux|convert|mplayer|iptables|svn|'
                      r'docker|kubectl|systemctl|service|crontab|bash|sh|zsh|seq|bc|diff|file|stat|tee|nohup|time|man|which|whoami|ping|dig|host|nslookup|'
                      r'zip|unzip|gzip|gunzip|bzip2|xz|7z|base64|md5sum|sha\d+sum|less|more|strings|od|hexdump|xxd|jq|make|gcc|npm|pip|java|mysql|psql|sqlite3)\b)', re.M)
def spam_eval(*texts):
    t = ' '.join(x or '' for x in texts).lower()
    strong = sorted({p for p in STRONG if re.search(p, t)})
    weak = sorted({p for p in WEAK if re.search(p, t)})
    code = texts[0] or ''
    shellish = bool(SHELLISH.search(code))
    if len(strong) >= 2 or (len(strong) == 1 and not shellish):
        return 'spam', strong + weak
    if strong or len(weak) >= 2:
        return 'review', strong + weak
    return 'ok', []

# ---------------- HTML helpers ----------------
def text_of(el):
    if el is None: return None
    for br in el.find_all('br'): br.replace_with('\n')
    return el.get_text()

def desc_text(el):
    if el is None: return None
    parts = []
    ps = el.find_all('p')
    if ps:
        for p in ps:
            parts.append(norm_ws(p.get_text(' ')))
        # include trailing inline <code> blocks not inside <p>
        for c in el.find_all('code', recursive=False):
            parts.append(norm_ws(c.get_text()))
    else:
        parts.append(norm_ws(el.get_text(' ')))
    out = '\n\n'.join(x for x in parts if x)
    return out or None

DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
ERROR_TITLE = re.compile(r'(404|not found|page not found|error|oops|forbidden|suspended|maintenance|wayback machine)', re.I)

def parse_view(path, url_id):
    h = open(path, 'rb').read().decode('utf-8', 'replace')
    soup = BeautifulSoup(h, 'lxml')
    title_tag = soup.title.get_text().strip() if soup.title else ''
    rec = dict(id=url_id)
    if not title_tag and len(h) < 2000:
        return None, 'empty_or_truncated_capture'
    if re.search(r'<meta[^>]+http-equiv=["\']?refresh', h, re.I) and 'num-votes' not in h:
        return None, 'redirect_or_interstitial'
    has_id = re.search(r'(num-votes|vote-up|toggle-favourite)-%d\b' % url_id, h) is not None
    main = soup.find(id='terminal-display-main') or soup
    cmd_el = main.find(class_='command')
    if not has_id:
        if ERROR_TITLE.search(title_tag) or cmd_el is None:
            return None, 'soft_error_page(title=%r)' % title_tag[:80]
        return None, 'id_mismatch(no element for url id)'
    if cmd_el is None:
        return None, 'missing_command_element'
    rec['code'] = html.unescape(text_of(cmd_el)).strip('\n')
    h1 = main.find('h1')
    t = norm_ws(h1.get_text()) if h1 else ''
    if not t:
        t = re.sub(r'\s*\|\s*(Command-line Fu|commandlinefu\.com)\s*$', '', title_tag).strip()
    rec['title'] = t or None
    d = main.find(class_='description')
    rec['description_original'] = desc_text(d)
    nv = soup.find(id='num-votes-%d' % url_id)
    rec['votes'] = int(nv.get_text().strip()) if nv and re.fullmatch(r'-?\d+', nv.get_text().strip()) else None
    a = main.find(class_='author')
    al = a.find('a', href=re.compile(r'/commands/by/')) if a else None
    rec['author'] = al.get_text().strip() if al else None
    de = main.find(class_='date')
    m = DATE_RE.search(de.get_text()) if de else None
    rec['date'] = m.group(1) if m else None
    if not rec['code'].strip():
        return None, 'empty_command'
    return rec, None

def parse_listing(path):
    """Parse 2009-2013 style listing pages (tag listings). Returns list of per-command dicts."""
    h = open(path, 'rb').read().decode('utf-8', 'replace')
    soup = BeautifulSoup(h, 'lxml')
    out = []
    for ol in soup.find_all(class_='one-liner'):
        nv = ol.find(id=re.compile(r'^num-votes-\d+$'))
        summ = ol.find(class_='summary')
        link = summ.find('a', href=re.compile(r'/commands/view/\d+')) if summ else None
        if not nv or not link: continue
        cid = int(nv['id'].split('-')[-1])
        lid = int(re.search(r'/commands/view/(\d+)', link['href']).group(1))
        r = dict(id=cid, link_id=lid, title=norm_ws(link.get_text()))
        c = ol.find(class_='command')
        r['code'] = html.unescape(text_of(c)).strip('\n') if c else None
        r['description_original'] = desc_text(ol.find(class_='description'))
        v = nv.get_text().strip(); r['votes'] = int(v) if re.fullmatch(r'-?\d+', v) else None
        a = ol.find(class_='author'); al = a.find('a', href=re.compile('/commands/by/')) if a else None
        r['author'] = al.get_text().strip() if al else None
        de = ol.find(class_='date'); m = DATE_RE.search(de.get_text()) if de else None
        r['date'] = m.group(1) if m else None
        tags = None; tags_kind = None
        fdivs = [(f, 'per_command_tags_block') for f in ol.find_all(class_='functions')]
        # 2016+ layout keeps the per-command meta (Functions/Tags) inside an HTML comment in the same <li>
        for cm in ol.find_all(string=lambda x: isinstance(x, Comment)):
            if 'Tags:' in cm or 'functions' in cm:
                fdivs += [(f, 'per_command_tags_block_html_comment') for f in BeautifulSoup(str(cm), 'lxml').find_all(class_='functions')]
        for fdiv, kind in fdivs:
            if fdiv.get_text().strip().startswith('Tags:'):
                tags = [] if tags is None else tags; tags_kind = kind
                for ta in fdiv.find_all('a', href=re.compile(r'/commands/tagged/\d+/')):
                    mm = re.search(r'/commands/tagged/(\d+)/([^/"?#]+)', ta['href'])
                    tags.append((int(mm.group(1)), mm.group(2), norm_ws(ta.get_text())))
        r['tags_block'] = tags  # None = no Tags: block on this block
        r['tags_kind'] = tags_kind
        out.append(r)
    return out

def sidebar_tag_names(path):
    """Sitewide tag cloud: used ONLY for tag taxonomy names, never for associations."""
    h = open(path, 'rb').read().decode('utf-8', 'replace')
    return [(int(a), b, norm_ws(re.sub('<[^>]+>', '', c))) for a, b, c in
            re.findall(r'href="(?:http://www\.commandlinefu\.com)?/commands/tagged/(\d+)/([^/"?#]+)"[^>]*>(.*?)</a>', h, re.S)]

# ---------------- provenance index of wayback fetches ----------------
prov = {}
for lf in [os.path.join(RAW, 'wayback_html', 'fetch_log.tsv')]:
    if os.path.exists(lf):
        for line in open(lf):
            p = line.rstrip('\n').split('\t')
            if len(p) >= 3:
                code, eff = p[2].split(' ', 1)
                prov[p[0]] = dict(requested=p[1], http=code, effective=eff)
samples_meta = json.load(open(os.path.join(RAW, 'wayback_html', 'samples', 'samples_meta.json')))
def capture_ts(rel, eff=None):
    m = re.search(r'/web/(\d{14})', eff or '')
    if m: return m.group(1)
    m = re.search(r'_(\d{14})\.html$', rel)
    return m.group(1) if m else None

# ---------------- 1. HF base ----------------
hf = json.load(open(os.path.join(RAW, 'hf', 'cli_commands_explained.json')))
S('hf_rows_total', len(hf))
hf_by_id = collections.defaultdict(list)
for idx, r in enumerate(hf):
    m = re.search(r'commandlinefu\.com/commands/view/(\d+)', r.get('url') or '')
    if not m:
        S('hf_rows_non_commandlinefu'); EXC('hf', 'row%d' % idx, 'not_commandlinefu_source(url=%s)' % (r.get('url') or '')[:80], 'excluded_out_of_scope'); continue
    uid = int(m.group(1))
    if r.get('id') is not None and int(r['id']) != uid:
        S('hf_rows_id_mismatch'); EXC('hf', 'row%d' % idx, 'id_field_%s_vs_url_id_%d' % (r['id'], uid), 'quarantined_mismatch'); continue
    hf_by_id[uid].append((idx, r))
S('hf_commandlinefu_rows', sum(len(v) for v in hf_by_id.values())); S('hf_unique_ids', len(hf_by_id))

corpus = {}
conflicts = []
def code_eq(a, b): return norm_ws(a) == norm_ws(b)
for uid, rows in hf_by_id.items():
    base = rows[0][1]
    for idx, r in rows[1:]:
        S('hf_duplicate_rows')
        if not code_eq(r['code'], base['code']) or norm_ws(r['title']) != norm_ws(base['title']):
            conflicts.append(dict(id=uid, kind='hf_internal_duplicate_conflict', a=dict(row=rows[0][0], title=base['title'], code=base['code']), b=dict(row=idx, title=r['title'], code=r['code'])))
        EXC('hf', 'row%d' % idx, 'duplicate_row_for_id_%d' % uid, 'deduplicated(kept row %d)' % rows[0][0])
    ai = bool(base.get('ai_generated_description'))
    corpus[uid] = dict(id=uid, url=base['url'], title=base['title'], code=base['code'],
                       description_original=None if ai else base['description'],
                       description_original_source=None if ai else 'hf',
                       description_ai=base['description'] if ai else None,
                       votes=base.get('votes'), votes_source='hf' if base.get('votes') is not None else None,
                       author=base.get('author') or None, date=base.get('date') or None,
                       sources=['hf'], tag_status='unknown', tags=[])

# ---------------- 3. Wayback view pages ----------------
wb_view_records = {}
view_files = sorted(glob.glob(os.path.join(RAW, 'wayback_html', 'views', '*.html')))
view_files += [os.path.join(RAW, 'wayback_html', 'samples', f) for f, m in samples_meta.items() if m['kind'] == 'view']
for vf in view_files:
    rel = os.path.relpath(vf, os.path.join(RAW, 'wayback_html'))
    base = os.path.basename(vf)
    if rel.startswith('samples/'):
        uid = samples_meta[base]['command_id']; ts = samples_meta[base]['capture_ts']; src_url = samples_meta[base]['url']
    else:
        uid = int(base.split('_')[0]); p = prov.get(rel, {}); ts = capture_ts(rel, p.get('effective')); src_url = p.get('requested')
    S('wb_view_files_parsed_attempted')
    rec, err = parse_view(vf, uid)
    if err:
        S('wb_view_rejected'); EXC('wayback_view', uid, err, 'quarantined_raw_preserved', raw_path='raw/wayback_html/' + rel); continue
    rec['capture_ts'] = ts; rec['raw_path'] = 'raw/wayback_html/' + rel; rec['source_url'] = src_url
    S('wb_view_parsed_ok')
    wb_view_records.setdefault(uid, []).append(rec)

def merge_wb(uid, rec, src):
    if uid in corpus:
        c = corpus[uid]
        if not code_eq(c['code'], rec['code']):
            conflicts.append(dict(id=uid, kind='code_differs', base_source=c['sources'][0], base=c['code'], other_source=src, other=rec['code'], capture_ts=rec.get('capture_ts')))
        if rec.get('title') and c['title'] and norm_ws(c['title']) != norm_ws(rec['title']):
            conflicts.append(dict(id=uid, kind='title_differs', base=c['title'], other=rec['title'], other_source=src, capture_ts=rec.get('capture_ts')))
        if rec.get('votes') is not None and c.get('votes') is not None and rec['votes'] != c['votes']:
            conflicts.append(dict(id=uid, kind='votes_temporal', base=c['votes'], base_source=c['votes_source'], other=rec['votes'], other_source=src, capture_ts=rec.get('capture_ts')))
        for f in ('author', 'date'):
            if rec.get(f) and c.get(f) and norm_ws(str(rec[f])) != norm_ws(str(c[f])):
                conflicts.append(dict(id=uid, kind=f + '_differs', base=c[f], other=rec[f], other_source=src, capture_ts=rec.get('capture_ts')))
            if rec.get(f) and not c.get(f): c[f] = rec[f]
        if rec.get('description_original') and not c.get('description_original'):
            c['description_original'] = rec['description_original']; c['description_original_source'] = src + '@' + str(rec.get('capture_ts'))
            S('ai_description_replaced_by_verified_original' if c.get('description_ai') else 'original_description_filled')
        if src not in c['sources']: c['sources'].append(src)
    else:
        corpus[uid] = dict(id=uid, url='http://www.commandlinefu.com/commands/view/%d' % uid, title=rec.get('title'), code=rec['code'],
                           description_original=rec.get('description_original'),
                           description_original_source=(src + '@' + str(rec.get('capture_ts'))) if rec.get('description_original') else None,
                           description_ai=None, votes=rec.get('votes'), votes_source=(src + '@' + str(rec.get('capture_ts'))) if rec.get('votes') is not None else None,
                           author=rec.get('author'), date=rec.get('date'), sources=[src], tag_status='unknown', tags=[])
        S('added_from_' + src)

for uid, recs in wb_view_records.items():
    recs.sort(key=lambda r: r.get('capture_ts') or '')
    for r in recs: merge_wb(uid, r, 'wayback_view')

# ---------------- 4. Tag taxonomy + associations ----------------
tags = {}  # id -> dict
def tag_add(tid, slug, name=None, src=None):
    t = tags.setdefault(tid, dict(tag_id=tid, slugs=set(), names=collections.Counter(), evidence=set()))
    if slug: t['slugs'].add(slug)
    if name: t['names'][name] += 1
    if src: t['evidence'].add(src)
for line in open(os.path.join(RAW, 'cdx', 'tag_all.txt')):
    m = re.search(r'/commands/tagged/(\d+)/([^/\s?#]+)', line)
    if m: tag_add(int(m.group(1)), m.group(2), None, 'cdx_url')
S('tag_ids_from_cdx', len(tags))

assoc = {}  # (cid, tid) -> evidence list
tag_obs = {}  # cid -> list of (capture, set of tag ids) from per-command Tags blocks
listing_files = sorted(glob.glob(os.path.join(RAW, 'wayback_html', 'tags', '*.html')))
listing_files += [os.path.join(RAW, 'wayback_html', 'samples', f) for f, m in samples_meta.items() if m['kind'] == 'tag_listing']
pages_seen = {}
for lf in listing_files:
    rel = os.path.relpath(lf, os.path.join(RAW, 'wayback_html')); base = os.path.basename(lf)
    if rel.startswith('samples/'):
        sm = samples_meta[base]; page_tid = sm['tag_id']; offset = sm.get('offset', 0); ts = sm['capture_ts']; src_url = sm['url']
    else:
        m = re.match(r'(\d+)_(.+?)((?:_o\d+)*)\.html$', base)
        page_tid = int(m.group(1)); offs = [int(x) for x in re.findall(r'_o(\d+)', m.group(3))]; offset = offs[-1] if offs else 0
        p = prov.get(rel, {}); ts = capture_ts(rel, p.get('effective')); src_url = p.get('requested')
    S('tag_pages_parse_attempted')
    for slug_, name_ in [(b, c) for a, b, c in sidebar_tag_names(lf) if a]:
        pass
    for a, b, c in sidebar_tag_names(lf):
        tag_add(a, b, c if c else None, 'anchor_text')
    htxt = open(lf, 'rb').read().decode('utf-8', 'replace')
    eff = (prov.get(rel) or {}).get('effective') or ''
    bu = re.search(r'name="base-url" value="/commands/tagged/(\d+)/', htxt)
    if eff and not re.search(r'/commands/tagged/%d(/|$)' % page_tid, eff):
        S('tag_pages_redirected_elsewhere'); EXC('wayback_tag_page', rel, 'redirect_or_wrong_target(effective=%s)' % eff[:200], 'quarantined_raw_preserved', raw_path='raw/wayback_html/' + rel); continue
    if bu and int(bu.group(1)) != page_tid:
        S('tag_pages_identity_mismatch'); EXC('wayback_tag_page', rel, 'base_url_tag_%s_vs_requested_%d' % (bu.group(1), page_tid), 'quarantined_mismatch', raw_path='raw/wayback_html/' + rel); continue
    tm = re.search(r'Commands tagged .*?\((\d+)\)', htxt); listing_total = int(tm.group(1)) if tm else None
    blocks = parse_listing(lf)
    if not blocks:
        S('tag_pages_no_command_blocks'); EXC('wayback_tag_page', rel, 'no_parseable_command_blocks(soft_error/empty/unsupported_layout)', 'quarantined_raw_preserved', raw_path='raw/wayback_html/' + rel); continue
    S('tag_pages_parsed_ok')
    pages_seen[rel] = dict(tag_id=page_tid, offset=offset, capture_ts=ts, n=len(blocks), listing_total_on_page=listing_total,
                           effective_url=eff or src_url, n_with_tags_block=sum(1 for b in blocks if b['tags_block'] is not None))
    if listing_total is not None and offset == 0:
        S('tag_listings_complete_single_page' if listing_total == len(blocks) else 'tag_listings_needing_pagination_not_fetched')
    for b in blocks:
        if b['id'] != b['link_id']:
            EXC('wayback_tag_page', '%s#%d' % (rel, b['id']), 'block_vote_id_%d_vs_link_id_%d' % (b['id'], b['link_id']), 'quarantined_mismatch'); continue
        ev = dict(source_url=src_url, capture_ts=ts, raw_path='raw/wayback_html/' + rel)
        assoc.setdefault((b['id'], page_tid), []).append(dict(ev, kind='listed_on_tag_page'))
        if b['tags_block'] is not None:
            tag_obs.setdefault(b['id'], []).append((ts, sorted({t[0] for t in b['tags_block']})))
            for tid, slug, name in b['tags_block']:
                tag_add(tid, slug, name, 'per_command_block')
                assoc.setdefault((b['id'], tid), []).append(dict(ev, kind=b['tags_kind']))
        b2 = dict(b); b2['capture_ts'] = ts
        merge_wb(b['id'], b2, 'wayback_tag_listing')

# sitewide tag clouds on view/sample pages -> names only
for f, m in samples_meta.items():
    for a, b, c in sidebar_tag_names(os.path.join(RAW, 'wayback_html', 'samples', f)):
        tag_add(a, b, c or None, 'anchor_text')

# tag status per command
for cid, c in corpus.items():
    tids = sorted({tid for (x, tid) in assoc if x == cid})
    if cid in tag_obs:
        sets = {tuple(s) for _, s in tag_obs[cid]}
        c['tags'] = tids
        c['tag_status'] = 'observed_full_block' if any(sets) else 'observed_no_tags'
        if len(sets) > 1:
            conflicts.append(dict(id=cid, kind='tag_set_temporal', observations=tag_obs[cid]))
    elif tids:
        c['tags'] = tids; c['tag_status'] = 'partial_listing_membership'
    else:
        c['tag_status'] = 'unknown'

# ---------------- 5. supplements: tg123, flatcap ----------------
tg_ids = {}
tg_files = sorted(glob.glob(os.path.join(RAW, 'tg123', '_data', '*.yaml')))
S('tg123_yaml_files', len(tg_files))
for f in tg_files:
    rel = 'raw/tg123/_data/' + os.path.basename(f)
    try:
        y = yaml.safe_load(open(f, encoding='utf-8'))
    except Exception as e:
        S('tg123_yaml_parse_error'); EXC('tg123', os.path.basename(f), 'yaml_parse_error:%s' % str(e)[:80], 'quarantined_raw_preserved', raw_path=rel); continue
    if not isinstance(y, dict) or not isinstance(y.get('commandlinefu_id'), int) or not y.get('command'):
        S('tg123_missing_required'); EXC('tg123', os.path.basename(f), 'missing_id_or_command', 'quarantined_raw_preserved', raw_path=rel); continue
    cid = y['commandlinefu_id']; cmd = str(y['command'])
    verdict, hits = spam_eval(cmd, os.path.basename(f), str(y.get('summary') or ''))
    if verdict == 'spam':
        S('tg123_spam_quarantined'); EXC('tg123', os.path.basename(f), 'spam:' + ','.join(hits), 'quarantined_spam_raw_preserved', raw_path=rel); continue
    if verdict == 'review':
        S('tg123_spam_review'); EXC('tg123', os.path.basename(f), 'possible_spam:' + ','.join(hits), 'review_not_in_clean', raw_path=rel); continue
    if cid <= 0:
        S('tg123_invalid_id'); EXC('tg123', os.path.basename(f), 'invalid_id_%d' % cid, 'quarantined_raw_preserved', raw_path=rel); continue
    if cid in tg_ids:
        S('tg123_duplicate_id'); EXC('tg123', os.path.basename(f), 'duplicate_id_%d' % cid, 'deduplicated', raw_path=rel)
        continue
    tg_ids[cid] = dict(code=cmd, raw_path=rel, hide=bool(y.get('hide')), shellish=bool(SHELLISH.search(cmd)))
S('tg123_unique_valid_ids', len(tg_ids))
for cid, t in tg_ids.items():
    if cid in corpus:
        S('tg123_overlap_with_corpus')
        if code_eq(corpus[cid]['code'], t['code']): S('tg123_code_matches_corpus')
        else:
            S('tg123_code_differs'); conflicts.append(dict(id=cid, kind='code_differs', base_source=corpus[cid]['sources'][0], base=corpus[cid]['code'], other_source='tg123', other=t['code']))
        if 'tg123' not in corpus[cid]['sources']: corpus[cid]['sources'].append('tg123')
    elif not t['shellish']:
        S('tg123_only_not_shellish_review'); EXC('tg123', cid, 'tg123_only_code_not_shell_like' + ('_hidden' if t['hide'] else ''), 'review_not_in_clean', raw_path=t['raw_path'])
    else:
        corpus[cid] = dict(id=cid, url='http://www.commandlinefu.com/commands/view/%d' % cid, title=None, code=t['code'],
                           description_original=None, description_original_source=None, description_ai=None,
                           votes=None, votes_source=None, author=None, date=None, sources=['tg123'], tag_status='unknown', tags=[],
                           completeness='supplement_code_only')
        S('added_from_tg123')

fc_dir = os.path.join(ROOT, 'raw', 'flatcap', 'extracted', 'commandlinefu')
for f in sorted(glob.glob(os.path.join(fc_dir, '*.html'))):
    m = re.match(r'0*(\d+)_', os.path.basename(f))
    if not m: continue
    S('flatcap_files_parsed')
    cid = int(m.group(1))
    soup = BeautifulSoup(open(f, encoding='utf-8', errors='replace').read(), 'lxml')
    mainc = soup.find(id='terminal-display-main'); ce = mainc.find(class_='command') if mainc else None
    if ce is None:
        S('flatcap_no_command'); EXC('flatcap', os.path.basename(f), 'no_main_command', 'quarantined_raw_preserved'); continue
    code = norm_ws(ce.get_text()); title = norm_ws(soup.title.get_text()) if soup.title else None
    if cid in corpus:
        S('flatcap_overlap')
        if code_eq(corpus[cid]['code'], code): S('flatcap_code_matches_corpus')
        else:
            S('flatcap_code_differs_whitespace_normalised'); conflicts.append(dict(id=cid, kind='code_differs', base_source=corpus[cid]['sources'][0], base=corpus[cid]['code'], other_source='flatcap(reformatted html)', other=code))
        if 'flatcap' not in corpus[cid]['sources']: corpus[cid]['sources'].append('flatcap')
    else:
        corpus[cid] = dict(id=cid, url='http://www.commandlinefu.com/commands/view/%d' % cid, title=title, code=code,
                           description_original=None, description_original_source=None, description_ai=None, votes=None, votes_source=None,
                           author=None, date=None, sources=['flatcap'], tag_status='unknown', tags=[], completeness='supplement_title_code_only')
        S('added_from_flatcap')

# ---------------- spam + required-content validation on corpus ----------------
clean = {}
for cid, c in sorted(corpus.items()):
    v, hits = spam_eval(c['code'], c.get('title'), c.get('description_original'))
    if v == 'spam':
        S('corpus_spam_quarantined'); EXC(c['sources'][0], cid, 'spam:' + ','.join(hits), 'quarantined_spam'); continue
    if v == 'review':
        S('corpus_spam_review'); EXC(c['sources'][0], cid, 'possible_spam:' + ','.join(hits), 'review_kept_in_clean_flagged'); c['review_flag'] = 'possible_spam'
    if not (c.get('code') or '').strip():
        S('corpus_missing_code'); EXC(c['sources'][0], cid, 'missing_code', 'quarantined'); continue
    c.setdefault('completeness', 'full' if c.get('title') else 'partial')
    c['has_newline_in_code'] = '\n' in c['code']
    c['html_entity_residue'] = bool(re.search(r'&(amp|lt|gt|quot|#\d+);', c['code']))
    if c['html_entity_residue']: S('corpus_code_with_entity_residue_flagged')
    if c['has_newline_in_code']: S('corpus_code_multiline')
    if c.get('date') and not re.match(r'^\d{4}-\d{2}-\d{2}', str(c['date'])): S('corpus_bad_date_format')
    clean[cid] = c

# tag FK check
missing_fk = sorted({tid for (cid, tid) in assoc if tid not in tags})
S('assoc_tag_fk_missing', len(missing_fk))
S('clean_commands', len(clean))
S('clean_with_any_tag_evidence', sum(1 for c in clean.values() if c['tag_status'] != 'unknown'))
S('clean_tag_status_unknown', sum(1 for c in clean.values() if c['tag_status'] == 'unknown'))
S('clean_ai_description_only', sum(1 for c in clean.values() if c.get('description_ai') and not c.get('description_original')))
S('clean_original_description', sum(1 for c in clean.values() if c.get('description_original')))
S('conflicts_total', len(conflicts))
for k, n in collections.Counter(x['kind'] for x in conflicts).items(): S('conflicts_' + k, n)
S('exclusions_total', len(exclusions))
S('associations_total', len(assoc))
S('associations_commands', len({c for c, _ in assoc}))
S('tags_total', len(tags))
S('tags_with_name', sum(1 for t in tags.values() if t['names']))

# ---------------- write outputs ----------------
with open(os.path.join(CLEAN, 'commands.jsonl'), 'w', encoding='utf-8') as f:
    for cid, c in sorted(clean.items()):
        f.write(json.dumps(c, ensure_ascii=False) + '\n')
with open(os.path.join(CLEAN, 'tags.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['tag_id', 'slug', 'other_slugs', 'name', 'name_variants', 'evidence'])
    for tid, t in sorted(tags.items()):
        sl = sorted(t['slugs']); name = t['names'].most_common(1)[0][0] if t['names'] else ''
        w.writerow([tid, sl[0] if sl else '', '|'.join(sl[1:]), name, '|'.join(n for n in t['names'] if n != name), '|'.join(sorted(t['evidence']))])
with open(os.path.join(CLEAN, 'command_tags.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['command_id', 'tag_id', 'evidence_kind', 'capture_ts', 'source_url', 'raw_path', 'command_in_clean'])
    for (cid, tid), evs in sorted(assoc.items()):
        for e in evs:
            w.writerow([cid, tid, e['kind'], e['capture_ts'], e['source_url'], e['raw_path'], int(cid in clean)])
with open(os.path.join(CLEAN, 'conflicts.jsonl'), 'w', encoding='utf-8') as f:
    for x in conflicts: f.write(json.dumps(x, ensure_ascii=False) + '\n')
with open(os.path.join(MAN, 'exclusions.jsonl'), 'w', encoding='utf-8') as f:
    for x in exclusions: f.write(json.dumps(x, ensure_ascii=False) + '\n')
with open(os.path.join(MAN, 'tag_pages_parsed.json'), 'w') as f: json.dump(pages_seen, f, indent=1)

db = os.path.join(CLEAN, 'commandlinefu.sqlite')
if os.path.exists(db): os.remove(db)
con = sqlite3.connect(db); cu = con.cursor()
cu.executescript('''
PRAGMA foreign_keys=ON;
CREATE TABLE tags(tag_id INTEGER PRIMARY KEY, slug TEXT, other_slugs TEXT, name TEXT, evidence TEXT);
CREATE TABLE commands(id INTEGER PRIMARY KEY, url TEXT, title TEXT, code TEXT NOT NULL, description_original TEXT, description_original_source TEXT,
  description_ai TEXT, votes INTEGER, votes_source TEXT, author TEXT, date TEXT, sources TEXT, tag_status TEXT, completeness TEXT, review_flag TEXT);
CREATE TABLE command_tags(command_id INTEGER, tag_id INTEGER REFERENCES tags(tag_id), evidence_kind TEXT, capture_ts TEXT, source_url TEXT, raw_path TEXT);
CREATE TABLE conflicts(id INTEGER, kind TEXT, json TEXT);
CREATE TABLE exclusions(source TEXT, key TEXT, reason TEXT, disposition TEXT, raw_path TEXT);
''')
for tid, t in sorted(tags.items()):
    sl = sorted(t['slugs'])
    cu.execute('INSERT INTO tags VALUES(?,?,?,?,?)', (tid, sl[0] if sl else None, '|'.join(sl[1:]), t['names'].most_common(1)[0][0] if t['names'] else None, '|'.join(sorted(t['evidence']))))
for cid, c in sorted(clean.items()):
    cu.execute('INSERT INTO commands VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', (cid, c['url'], c.get('title'), c['code'], c.get('description_original'), c.get('description_original_source'),
               c.get('description_ai'), c.get('votes'), c.get('votes_source'), c.get('author'), c.get('date'), ','.join(c['sources']), c['tag_status'], c.get('completeness'), c.get('review_flag')))
for (cid, tid), evs in sorted(assoc.items()):
    for e in evs: cu.execute('INSERT INTO command_tags VALUES(?,?,?,?,?,?)', (cid, tid, e['kind'], e['capture_ts'], e['source_url'], e['raw_path']))
for x in conflicts: cu.execute('INSERT INTO conflicts VALUES(?,?,?)', (x['id'], x['kind'], json.dumps(x, ensure_ascii=False)))
for x in exclusions: cu.execute('INSERT INTO exclusions VALUES(?,?,?,?,?)', (x['source'], x['key'], x['reason'], x['disposition'], x.get('raw_path')))
con.commit()
fk = cu.execute('PRAGMA foreign_key_check').fetchall(); S('sqlite_fk_violations', len(fk))
S('sqlite_integrity_ok', int(cu.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'))
con.close()
json.dump(stats, open(os.path.join(MAN, 'processing_stats.json'), 'w'), indent=1)
for k, v in stats.items(): print(k, v)
