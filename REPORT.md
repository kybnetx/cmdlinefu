# commandlinefu.com archive bundle: acquisition and verification report

Retrieval date: 2026-11-17 (revision 3: 17 title fixes, 38 more Wayback pages, third-party GROK mirror data verified and merged into one unified corpus). Revision 4 (2026-11-18): spam and garbage physically removed from the bundle; see "Spam purge (rev 4)". Scope: archival data and asset recovery only. Nothing was built or deployed, and no archived shell command was executed.

## Bottom line
- **One unified corpus:** `clean/` holds **14,806 commands** keyed by original commandlinefu ID.
  - **14,367 are evidence-backed.** They come from Hugging Face (base), tg123 YAML, flatcap HTML and our own Wayback captures.
  - **439 exist only in a third-party Grok-generated mirror site** (`raw/grok/`). They are marked `completeness = "third_party_only"`.
  - Third-party values are merged at the **lowest precedence**: they only fill empty fields, and every value they supply is marked. See "Third-party merge (GROK mirror site)" below.
- **Coverage is partial.** The Wayback Machine refused connections from the acquisition VM on 2026-11-17, first on port 80 and then on port 443. Per the two-failure rule, that route was stopped. A second short round that evening saved 38 more pages before port 443 was refused again. **4,565 Wayback fetch jobs remain pending** (3,813 tag-listing pages and 752 Wayback-only command pages; 179 jobs for spam pages were dropped in rev 4). They are resumable with `tools/wayback_fetch.sh`.
- **Tags:**
  - **Own evidence:** 1,284 command-tag pairs on 299 commands (about 2.0%), all with capture provenance (`tag_status = "observed_full_block"`).
  - **Third-party, unverified:** 16,836 more pairs on 6,016 commands (`tag_status = "third_party_unverified"`).
  - **Unknown:** the other 8,491 commands have `tag_status = "unknown"`, which means not recovered. It does not mean the command had no tags.
  - No tags were inferred, and the mirror site's "derived" (guessed) tags were not used.
- 5,006 records are logged in `manifests/exclusions.jsonl`: purged spam/garbage (IDs only), review items, duplicates, out-of-scope rows and rejected third-party tags.
- **Spam and garbage are deleted, not quarantined (rev 4).** 1,600 tg123 YAML files, 242 GROK pages, 143 third-party-only clean records, 18 spam comment blocks in flatcap pages, 548 spam URL lines and the two spam-laden upstream archives were removed. `manifests/spam_purge.json` keeps only IDs, categories and sha256 values; no spam text.
- `python3 tools/validate_unified.py` checks the merge rules and passes with 0 failures. It also confirmed that the merge overwrote none of the 14,367 evidence-backed records.
- This bundle is not claimed to be error-free or complete. The counts below are exact for what was acquired.

## Layout
| Path | Contents |
|---|---|
| `raw/` | Immutable acquisitions: HF JSON, CDX indices, Wayback HTML plus fetch logs, tg123 repo (spam YAMLs removed; upstream tarball deleted), flatcap tarball plus extract (spam comments removed), yedeying tarball |
| `clean/commands.jsonl` | Unified deduplicated corpus, one JSON object per command. Third-party values are marked per record (`sources`, `third_party_fields`, `third_party_checks`, `*_source`) |
| `clean/tags.csv` | Tag taxonomy: original tag_id, slug, name, evidence |
| `clean/command_tags.csv` | Association evidence rows: 19,925 rows for 18,120 unique pairs. 1,284 pairs have own capture evidence; 16,836 have only `evidence_kind = third_party_grok_mirror` with capture timestamp, URL and raw file |
| `clean/conflicts.jsonl` | Cross-source disagreements (155) |
| `clean/commandlinefu.sqlite` | Same data in tables tags, commands, command_tags, conflicts, exclusions (FKs enforced) |
| `manifests/sources.json` | Source URLs, licence, retrieval date, sha256, counts |
| `manifests/exclusions.jsonl` | Quarantine/exclusion log: source, key, reason, disposition, detail, raw_path |
| `manifests/processing_stats.json` | Machine-readable counts from the last processing run |
| `manifests/spam_purge.json` | Rev 4 purge log: removed files (sha256, size), per-item source/ID/category/basis, URL-list lines dropped. Contains no spam text |
| `manifests/wayback_pending_jobs.tsv` | 4,565 unfetched Wayback jobs (resumable) |
| `manifests/wayback_only_ids.tsv` | 773 command IDs with Wayback captures that are absent from HF (179 spam-page IDs dropped in rev 4) |
| `manifests/tag_pages_parsed.json` | Per-tag-page parse results (listing totals, effective URL, pagination state) |
| `manifests/asset_urls_todo.txt` | 44 CSS/JS/image URLs referenced by the archived pages, not yet fetched |
| `manifests/SHA256SUMS` | Checksums of every file in the bundle except itself |
| `raw/grok/` | Read-only page extract `grok_commands.jsonl` of the third-party mirror site, with spam/garbage pages removed (the site tarball was deleted in rev 4) |
| `assets/` | Recovered static assets: flatcap `style.css`, yedeying `css/bootstrap.css` and `css/style.css`, tg123 `wwwroot` (site.css, site.js, favicon.ico) |
| `tools/process.py`, `tools/wayback_fetch.sh`, `tools/grok/parse_grok.py`, `tools/validate_unified.py` | Processing pipeline (including the third-party merge), resumable fetcher, read-only GROK page extractor, and the invariant checker. Neither one executes archived commands |

## Acquisition counts by step (recommended order)
| Step | Attempted | Downloaded / parsed | Accepted into CLEAN | Quarantined / review | Failed / pending |
|---|---:|---:|---:|---:|---:|
| 1. HF JSON | 1 file, 16,098 rows | 16,098 rows | 14,041 unique IDs | 2,045 out of scope (cheat/cheatsheets), 12 duplicate rows, 6 kept flagged | 0 |
| 2. CDX indices | 3 queries | views 15,243 lines (14,806 IDs; 190 spam lines dropped in rev 4); tag 2,966 + 6,546 lines (2,944 tag IDs) | n/a (index only) | n/a | 0 |
| 3. Wayback-only command pages | 952 IDs in set difference (773 after the rev 4 spam purge) | 21 pages saved and parsed (25 view parses incl. samples, all OK) | 21 | 0 | 752 pending |
| 4. Tag listing pages | 3,865 tag listing jobs planned | 52 fetched + 1 sample = 53 attempted, 49 parsed OK | 1,284 unique pairs / 299 commands | 4 pages with no command blocks quarantined; 0 redirect or ID mismatches | 3,813 pending; 3 pages need pagination (tags 101 `size` 62, 102 `sort` 176, 104 `perl` 190; 25 on page 1) |
| 5a. tg123 YAML | 11,615 files (10,015 after rev 4) | 10,015 parsed | 304 new IDs (9,553 matched existing code) | 1,600 spam/garbage files deleted in rev 4; 30 review kept in raw (4 real commands flagged by weak rules, 26 non-shell-like but plausible or already in clean via other sources), 1 duplicate ID | 0 |
| 5b. flatcap HTML | 569 files | 569 parsed | 1 new ID (562 matched existing code) | 4 with no command | 0 |
| 5c. yedeying | 1 tarball | CSS extracted | data.js kept raw, not merged (no verifiable IDs) | — | — |
| 7. Third-party GROK mirror site | 1 tarball, 14,953 command pages (14,711 after rev 4) | 14,711 in extract | 439 new IDs; fills on 212 records; 16,836 unverified tag pairs | 242 spam/garbage pages deleted in rev 4; 1,062 tag chips rejected | 0 |
| 6. Assets | local repos | 6 asset files | n/a | n/a | 44 referenced Wayback asset URLs not fetched |

Wayback HTTP totals: 73 successful fetches logged (`raw/wayback_html/fetch_log.tsv`) plus 5 earlier samples. 16 failures are logged in `fetch_fail.tsv`, and 6 port-80 failures in `fetch_fail_round1_port80.tsv`. Both port-443 rounds were killed after refusals; no partial files were kept.

## Clean corpus composition
`grok_mirror` in `sources` means that the mirror site has the same command text. It corroborates the record but is not evidence on its own.

| Sources contributing | Commands |
|---|---:|
| hf + tg123 (+ grok_mirror) | 8,988 |
| hf (+ grok_mirror) | 4,218 |
| **grok_mirror only (third_party_only)** | **439** |
| hf + tg123 + flatcap (+ grok_mirror) | 471 |
| tg123 + grok_mirror | 198 |
| hf + wayback tag listing + tg123 (+ grok_mirror) | 191 |
| tg123 only | 93 |
| hf + wayback tag listing (+ grok_mirror) | 90 |
| hf + flatcap (+ grok_mirror) | 62 |
| other combinations | 56 |
| **Total** | **14,806** |

Descriptions: 10,379 commands have an original description, and 4,002 have only AI-generated text. AI text is stored in `description_ai` and never in `description_original`. `description_original_source` says where the original text came from: HF non-AI text (10,039), a Wayback capture (15, recorded as `wayback_view@<timestamp>`), or the third-party mirror site (325, recorded as `grok_mirror`). The mirror site's AI-written descriptions were not imported. tg123 summaries are Chinese translations, so they are never used as original descriptions.

## Validation performed
- **URL ID vs extracted ID:** every Wayback page and every flatcap file was checked against the ID in its URL or filename. For tag pages, the effective URL had to contain `/commands/tagged/<id>` with the expected ID. There were 0 mismatches and 0 redirects among the parsed tag pages.
- **Error, redirect and soft-200 checks:** pages without a command block (soft-200 or error) are quarantined. The 4 flatcap files with no command were quarantined.
- **Required content:** every clean record has an ID and a non-empty code field.
- **Escaping and newlines:** HTML entities are decoded once. 18 records still contain entity-like residue and are flagged with `html_entity_residue`; this may be literal text in the original. 2 records contain multi-line code (`has_newline_in_code`).
- **Duplicates:** 12 HF duplicate rows and 1 tg123 duplicate ID were deduplicated and logged.
- **Conflicts:** 155 cross-source disagreements are kept in `clean/conflicts.jsonl` and were not silently overwritten. They break down as follows:
  - 132 code differences (3 of them against `grok_mirror`);
  - 11 vote differences over time (temporal);
  - 9 tag-set differences between our own tag blocks and the mirror site;
  - 2 author differences;
  - 1 date difference (with `grok_mirror`). The earlier title conflict (ID 13) was a parser defect and disappeared with the title fix. HF is the primary value; the alternative value and its source are recorded.
- **Authors, votes, dates:** taken only from a source field. Fields with no source value are null. Nothing was fabricated, and HF dates are the uploader's estimates.
- **Titles (rev 2):** on 2009-layout view pages, `<h1>` is the site banner, so 17 commands (IDs 1, 5, 12, 20, 24–26, 28, 30, 32, 35, 43, 51, 54–56, 58) were titled "Command-line-fuAlpha". The parser now reads `h2#terminal-summary` and ignores the banner `<h1>`. All 17 titles were re-extracted from our own captures; no title still contains the banner.
- **Unified-merge invariants:** `tools/validate_unified.py` returned 0 failures. Every third-party value is listed in `third_party_fields` with its `*_source`. `third_party_unverified` tags have no own evidence, and own tag statuses are unchanged. jsonl and SQLite agree. With the pre-merge corpus as input, it confirmed that none of the 14,367 evidence-backed records lost or changed a value. A negative test with two deliberately altered values produced 2 failures, as expected.
- **Tag foreign keys:** all 19,925 association rows reference an existing tag and an existing clean command. SQLite `foreign_key_check` shows 0 violations, and `integrity_check` returned ok.
- **Pagination identity:** each listing records `listing_total` from the "Commands tagged X (N)" header. Listings with more than one page are marked incomplete, never complete.

## Tag semantics
- `tag_status = "observed_full_block"` (299): the command's own per-command Tags block was captured. These are original tag IDs and slugs, with `evidence_kind` `per_command_tags_block` or `per_command_tags_block_html_comment` (2016+ layout, where the block is inside an HTML comment). `listed_on_tag_page` rows are also included.
- `tag_status = "third_party_unverified"` (6,016): tags come only from the third-party mirror site's "original" tag chips, mapped to our taxonomy. Their evidence rows have `evidence_kind = third_party_grok_mirror`.
- `tag_status = "unknown"` (8,491): no per-command tag evidence was acquired. This is not the same as "no tags".
- Sitewide "Top Tags", `/commands/using/` words and meta keywords are **never** used as associations.
- 2,949 tags are in the taxonomy (2,944 from CDX tag URLs plus 5 seen in per-command blocks). 1,478 of them have a display name (from anchor text); the rest have only ID and slug.

## Spam and exclusion policy
- STRONG rules (luxury-brand, replica, outlet, dress, price-pattern terms and similar) mark an item as spam. Since rev 4, spam is **deleted** from `raw/` and logged only by ID (`disposition = removed_from_repository`, `reason = purged_spam` / `purged_garbage`).
- A WEAK-only hit (for example cheap, sale, discount, watch, or a single price) sends the item to review (`review_not_in_clean`) when it is a tg123-only item.
- For HF items, a weak hit means `review_kept_in_clean_flagged`. There are 6 such items (IDs 3562, 5085, 5737, 8478, 9495, 10218); they look like false positives and stay in CLEAN with a review flag.
- A tg123-only item must also have shell-like code, otherwise it goes to review.
- Every rule hit is listed in the `reason` field.
- Exclusion totals by disposition (rev 4): 2,045 out of scope, 1,842 removed from repository (1,600 tg123 + 242 grok_mirror), 1,062 rejected GROK tag chips (975 truncated slugs, 81 not in the taxonomy, 6 junk slugs), 30 review not in clean, 13 deduplicated, 6 review kept flagged, 8 quarantined (4 flatcap files with no command, 4 tag pages with no command blocks). Total: 5,006.

## Spam purge (rev 4, 2026-11-18)
Spam and garbage were **deleted** from the bundle and from the git repository (including its history). Nothing evidence-backed was removed: a before/after comparison shows exactly 143 records removed from `clean/commands.jsonl`, all `third_party_only`, and 0 other records changed. `tools/validate_unified.py` against the pre-merge corpus still reports 0 failures and all 14,367 evidence-backed records present and unchanged.

| What | Removed | Basis |
|---|---:|---|
| tg123 `_data/*.yaml` | 1,600 files | 1,302 STRONG-rule spam; 60 of 64 weak-rule review items (shop spam); 238 of 264 non-shell-like tg123-only items (shop names, keyboard mash, code identifiers). Kept: the 4 real commands whose IDs are in clean via HF, 17 items whose IDs are in clean via other sources, and 9 plausible commands (IDs 14311, 14353, 14414, 14723, 14865, 14886, 15024, 15042, 15301) |
| `raw/tg123_commandlinefu.cn-master.tar.gz` | 1 file | upstream tarball contained all the spam YAMLs; the cleaned extracted repo stays in `raw/tg123/` |
| GROK pages in `raw/grok/grok_commands.jsonl` | 242 pages | 93 STRONG-rule spam + 6 review (escorts, cannabis, archery shop, piracy, betting), and 143 third-party-only records reviewed by hand (escorts, real estate, SEO/link spam, casino/loans, news articles, box-office spam, password-unlocker adverts, essay spam, keyboard mash) |
| `raw/grok/commandlinefu-mirror-site.tar.xz` | 1 file | contained the spam pages; `tools/grok/parse_grok.py` can no longer be re-run from the bundle |
| flatcap pages (tarball repacked + `extracted/`) | 18 comment blocks in 16 pages | shop/replica/Taobao adverts posted as comments; command blocks untouched |
| URL lists | 548 lines | spam-page URLs whose slug is the spam title: `raw/cdx/views.txt` 190, `wayback_pending_jobs.tsv` 179, `wayback_only_ids.tsv` 179. URLs whose slug is a real command title were kept, so the real page can still be recovered |

Removed from clean (143 IDs): 1985, 3657, 5952, 5966, 6028, 6095, 6303, 6342, 6492, 6789, 6892, 6992, 7302, 10952, 13546, 18211, 18409, 19644, 21983, 23304, 25710, 25712, 25793–25796, 25802–25804, 25808–25810, 25815, 25817, 25818, 25821–25823, 25825, 25970, 26059, 26186, 26226, 26579, 26926, 27076, 27565, 27628, 27636, 27770, 27774, 27878, 27881, 27882, 27884–27889, 28150, 28804, 28805, 29066, 29241, 29268, 29972–29974, 30440, 30876, 30882, 30946, 31281, 31346, 31476, 31641, 31805, 31895, 32098, 33470, 33613, 33742, 33795, 33818, 33867, 34138, 34516, 34684, 34698, 34713, 34720, 34733, 34756, 34825, 34843, 35110, 35117, 35149, 35455, 36661, 36777, 36791, 36798, 36811, 36851, 36860, 37446, 38206, 38339, 38769, 38776, 39045, 39214, 39681, 40317, 40604, 40818, 40820, 40840, 41064, 41085, 41212, 41462, 41577, 41728, 41730, 42077, 42318, 42491, 42515, 42696, 42823, 42968, 43074, 43203, 43239, 43307, 43313, 43326, 43491, 43498, 43555.

Kept on purpose: the 6 HF items flagged by weak rules (IDs 3562, 5085, 5737, 8478, 9495, 10218) are real commands, and short legitimate third-party commands (`pushd .`, `ethtool eth0`, `ss -ltu`, fork-bomb variants, etc.) stay.

`tools/process.py` reads `manifests/spam_purge.json`, writes one exclusion row per purged item, and drops any purged GROK ID if it is ever re-introduced. The original sha256 of every deleted raw file and of both deleted archives is in `spam_purge.json` and `manifests/sources.json`.


## Remaining gaps (resumable)
1. 752 Wayback-only command pages are not fetched. Their IDs are in `manifests/wayback_only_ids.tsv` and their jobs in `wayback_pending_jobs.tsv`.
2. 3,813 tag-listing pages are not fetched, including offset/pagination pages. Verified tag coverage will stay about 2% until these are fetched.
3. Tags 101 (`size`), 102 (`sort`) and 104 (`perl`) still need their later listing pages.
4. 44 Wayback asset URLs (CSS/JS/images, `/css/browser_reset.css` etc.) are not fetched.
5. 187 HF IDs have no Wayback capture, so their original text cannot be cross-verified.
6. Comments were not acquired.
7. Not checked: archive.today, Common Crawl, GitLab.
8. 173 commands have no title and 93 no author. These are mostly tg123-only additions (a source that lacks these fields) and third-party records whose title was a "Comments (N)" heading or was truncated. Of the 773 Wayback-only IDs, 96 are still missing from the unified corpus.

To resume when Wayback is reachable, run from the bundle root:
`cut -f1,2 manifests/wayback_pending_jobs.tsv | tr '\t' '\n' | xargs -d '\n' -n2 -P3 tools/wayback_fetch.sh && python3 tools/process.py && python3 tools/validate_unified.py`

## Third-party merge (GROK mirror site)
**Source.** `raw/grok/commandlinefu-mirror-site.tar.xz` (deleted in rev 4 because it contained the spam pages; 7,897,452 bytes, sha256 `1a20b214014688fbe5550984721c64747370957f0ce8803ca593f2950c22a548`) is a static site that a third party generated with Grok on 2026-11-13, from a `commands.sqlite` that was not supplied. It includes no raw captures. `tools/grok/parse_grok.py` extracted all 14,953 command pages read-only into `raw/grok/grok_commands.jsonl` (0 parse failures). The site's AI descriptions and its "derived" (guessed) tags were not extracted.

**Verification against evidence we hold ourselves (step 6 of `tools/process.py`):**

| Check | Result |
|---|---|
| Code, on the 14,272 IDs shared with our evidence-backed records | 14,269 identical; 3 differ. Those 3 are logged as conflicts, and nothing else is taken from those pages |
| Title / author / date, where both sides have a value | 14,045 / 14,057 / 14,056 identical; 0 / 0 / 1 differ |
| Own tag pairs (1,284) also on the site | 1,079 (84%). 24 extra site pairs on 9 fully observed commands contradict our captured blocks; they are logged as `tags_differ`, and our blocks are kept |
| Third-party-only commands (439 after rev 4) whose ID is in the Wayback CDX index | 438 |
| …whose title matches the Wayback URL slug | 372. 67 have nothing to compare; 4 titles were truncated (e.g. "Create a new self" for `create-a-new-self-signed-certificate`) and are set to null |
| …whose code matches the copy in tg123 that we had excluded | 16 of 16 that exist in tg123 |
| Spam rules (the same as the evidence pipeline), then manual review (rev 4) | 93 spam and 6 review rejected by rules; 143 more removed after manual review; all 242 deleted from the extract |

**Merge rules:**
1. Evidence-backed values always win. A third-party value only fills an empty field, and only when the command text is identical.
2. **Fills.** Every filled field is listed in the record's `third_party_fields`; descriptions and votes also get `*_source = "grok_mirror"`.
   - 439 new records (`completeness = "third_party_only"`, with `third_party_checks`);
   - 197 titles, 212 authors, 212 dates and 212 vote counts for tg123-only records;
   - 113 original descriptions.
3. **Bad titles are dropped.** 88 "Comments (N)" headings and 6 truncated titles were set aside, and `title_issue` records why.
4. **Tags:**
   - Only complete slugs from our taxonomy are used.
   - The site links tags by slug only, and 42 slugs belong to several tag IDs. 2,319 such links were resolved in a fixed order: the ID already in the command's own block first, then the ID with the most own evidence, then the lowest ID. The candidates are written to the evidence row's `source_url`.
   - For commands with a captured tag block, only pairs that confirm it are added.
5. The rules are re-run on every `tools/process.py` run. `tools/validate_unified.py` checks them.

**How to read it.** Measured against our own evidence, the site is right about 84–99% of the time, depending on the field. Treat `third_party_only` records, `third_party_fields` and `third_party_unverified` tags as unverified until a Wayback capture confirms them.

## Licences and safety
HF is CC0 according to its card, tg123 is under the Unlicense, and flatcap and yedeying state no licence. The content was submitted by the community; keep author attribution and a credit to commandlinefu.com. **Do not run commands from this archive without reading them first.** Some are destructive.
