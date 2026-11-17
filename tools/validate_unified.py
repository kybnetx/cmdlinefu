"""Invariant checks for the unified corpus (clean/ after tools/process.py). Exit code 1 on any failure.

Usage: python3 tools/validate_unified.py [previous_commands.jsonl]
  With a previous commands.jsonl (the evidence-only corpus before the third-party merge), it also proves that
  the merge never overwrote or removed an evidence-backed value.
"""
import collections, csv, json, os, re, sqlite3, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
C = {r['id']: r for r in map(json.loads, open(os.path.join(ROOT, 'clean', 'commands.jsonl'), encoding='utf-8'))}
TAGS = {int(r['tag_id']) for r in csv.DictReader(open(os.path.join(ROOT, 'clean', 'tags.csv'), encoding='utf-8'))}
ROWS = list(csv.DictReader(open(os.path.join(ROOT, 'clean', 'command_tags.csv'), encoding='utf-8')))
GROK, TP = 'grok_mirror', 'third_party_grok_mirror'
fails = collections.Counter()
def check(cond, name):
    if not cond: fails[name] += 1

ev = collections.defaultdict(set)  # command -> evidence kinds
pairs = collections.defaultdict(set)
for r in ROWS:
    cid, tid = int(r['command_id']), int(r['tag_id'])
    check(tid in TAGS, 'tag_fk_missing')
    ev[cid].add(r['evidence_kind']); pairs[cid].add(tid)

for cid, c in C.items():
    check(isinstance(cid, int) and (c.get('code') or '').strip(), 'missing_id_or_code')
    check(not re.match(r'^Comments \(\d+\)$', c.get('title') or ''), 'comment_heading_title')
    check('Command-line-fuAlpha' not in (c.get('title') or ''), 'banner_title')
    check(not (c.get('description_ai') and c.get('description_original') == c.get('description_ai')), 'ai_text_in_original')
    tpf = set(c.get('third_party_fields') or [])
    check(bool(tpf) == (GROK in c['sources'] and bool(tpf)), 'third_party_fields_without_source')
    if tpf: check(GROK in c['sources'], 'third_party_fields_without_source')
    if c['sources'] == [GROK]:
        check(c.get('completeness') == 'third_party_only', 'third_party_only_label')
        check('code' in tpf, 'third_party_only_code_unmarked')
        for f in ('title', 'author', 'date', 'votes', 'description_original'):
            check(c.get(f) is None or f in tpf, 'third_party_only_field_unmarked:' + f)
    for f, srcf in (('description_original', 'description_original_source'), ('votes', 'votes_source')):
        if f in tpf: check(c.get(srcf) == GROK, 'third_party_value_source_unmarked:' + f)
        elif c.get(srcf) == GROK: check(False, 'grok_source_not_in_third_party_fields:' + f)
    st = c['tag_status']
    check(set(c.get('tags') or []) == pairs.get(cid, set()), 'tags_vs_association_rows')
    if st == 'third_party_unverified': check(ev.get(cid) == {TP}, 'third_party_status_has_own_evidence')
    if st == 'unknown': check(not c.get('tags'), 'unknown_status_with_tags')
    if st in ('observed_full_block', 'observed_no_tags'): check(ev.get(cid, {TP}) - {TP} or st == 'observed_no_tags', 'observed_status_without_own_evidence')
    if TP in ev.get(cid, ()): check(GROK in c['sources'], 'grok_tag_rows_without_grok_source')

con = sqlite3.connect(os.path.join(ROOT, 'clean', 'commandlinefu.sqlite'))
check(con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok', 'sqlite_integrity')
check(not con.execute('PRAGMA foreign_key_check').fetchall(), 'sqlite_fk')
check(con.execute('SELECT count(*) FROM commands').fetchone()[0] == len(C), 'sqlite_commands_count')
check(con.execute('SELECT count(*) FROM command_tags').fetchone()[0] == len(ROWS), 'sqlite_command_tags_count')
check(con.execute("SELECT count(*) FROM commands WHERE third_party_fields IS NOT NULL").fetchone()[0] == sum(1 for c in C.values() if c.get('third_party_fields')), 'sqlite_third_party_fields')

preserved = None
if len(sys.argv) > 1:
    P = {r['id']: r for r in map(json.loads, open(sys.argv[1], encoding='utf-8'))}
    changed = collections.Counter()
    for cid, p in P.items():
        if cid not in C: check(False, 'previous_record_removed'); continue
        for f, v in p.items():
            if f in ('sources', 'tags', 'tag_status'): continue
            if v is not None and C[cid].get(f) != v: check(False, 'evidence_value_overwritten:' + f); changed[f] += 1
        check(set(p['sources']) <= set(C[cid]['sources']), 'previous_source_dropped')
        check(set(p.get('tags') or []) <= set(C[cid].get('tags') or []), 'previous_tag_dropped')
        if p['tag_status'] != 'unknown': check(C[cid]['tag_status'] == p['tag_status'], 'own_tag_status_changed')
    preserved = dict(previous_records=len(P), all_present=all(i in C for i in P), overwritten=dict(changed))

out = dict(commands=len(C), association_rows=len(ROWS), failures=dict(fails), preservation=preserved)
print(json.dumps(out, indent=1))
sys.exit(1 if fails else 0)
