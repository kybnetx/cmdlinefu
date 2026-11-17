# commandlinefu.com archive bundle: acquisition and verification report

Retrieval date: 2026-11-17 (revision 2, same day: 17 title fixes, 38 more Wayback pages, labelled third-party GROK layer). Scope: archival data and asset recovery only. Nothing was built or deployed, and no archived shell command was executed.

## Bottom line
- The CLEAN corpus has **14,367 commands** keyed by original commandlinefu ID. They come from Hugging Face (base), tg123 YAML, flatcap HTML and Wayback captures.
- **Coverage is partial.** The Wayback Machine refused connections from the acquisition VM on 2026-11-17, first on port 80 and then on port 443. Per the two-failure rule, that route was stopped. A second short round that evening saved 38 more pages before port 443 was refused again. **4,744 Wayback fetch jobs remain pending** (3,813 tag-listing pages and 931 Wayback-only command pages). They are resumable with `tools/wayback_fetch.sh`.
- **Original tags are recovered for 299 commands (about 2.1%)**: 1,284 unique command-tag pairs across 429 tags, all with capture provenance. The other 14,068 commands have `tag_status = "unknown"`, which means not recovered. It does not mean the command had no tags. No tags were inferred.
- 3,702 records are logged in `manifests/exclusions.jsonl`. These are spam, review items, duplicates and out-of-scope rows. All raw evidence is kept under `raw/`.
- **Third-party layer:** `thirdparty/grok/` holds the usable parts of a third-party Grok-generated mirror site, labelled `third_party_unverified` and kept out of `clean/`. It contains 582 gap commands, 113 original descriptions and 17,921 tag pairs on 6,287 commands. See "Third-party GROK layer" below.
- This bundle is not claimed to be error-free or complete. The counts below are exact for what was acquired.

## Layout
| Path | Contents |
|---|---|
| `raw/` | Immutable acquisitions: HF JSON, CDX indices, Wayback HTML plus fetch logs, tg123 repo and tarball, flatcap tarball plus extract, yedeying tarball |
| `clean/commands.jsonl` | Clean deduplicated corpus, one JSON object per command |
| `clean/tags.csv` | Tag taxonomy: original tag_id, slug, name, evidence |
| `clean/command_tags.csv` | Association evidence rows (2,010 rows = 1,284 unique pairs) with capture timestamp, URL and raw file |
| `clean/conflicts.jsonl` | Cross-source disagreements (142) |
| `clean/commandlinefu.sqlite` | Same data in tables tags, commands, command_tags, conflicts, exclusions (FKs enforced) |
| `manifests/sources.json` | Source URLs, licence, retrieval date, sha256, counts |
| `manifests/exclusions.jsonl` | Quarantine/exclusion log: source, key, reason, disposition, detail, raw_path |
| `manifests/processing_stats.json` | Machine-readable counts from the last processing run |
| `manifests/wayback_pending_jobs.tsv` | 4,744 unfetched Wayback jobs (resumable) |
| `manifests/wayback_only_ids.tsv` | 952 command IDs with Wayback captures that are absent from HF |
| `manifests/tag_pages_parsed.json` | Per-tag-page parse results (listing totals, effective URL, pagination state) |
| `manifests/asset_urls_todo.txt` | 44 CSS/JS/image URLs referenced by the archived pages, not yet fetched |
| `manifests/SHA256SUMS` | Checksums of every file in the bundle except itself |
| `raw/grok/` | Third-party mirror site tarball (as supplied) and its read-only page extract `grok_commands.jsonl` |
| `thirdparty/grok/` | **Third-party, unverified** layer: gap commands, description supplement, tag pairs, exclusions, own SQLite. Never merged into `clean/` |
| `assets/` | Recovered static assets: flatcap `style.css`, yedeying `css/bootstrap.css` and `css/style.css`, tg123 `wwwroot` (site.css, site.js, favicon.ico) |
| `tools/process.py`, `tools/wayback_fetch.sh`, `tools/grok/` | Processing pipeline, resumable fetcher, and the GROK extract/layer builders. Neither one executes archived commands |

## Acquisition counts by step (recommended order)
| Step | Attempted | Downloaded / parsed | Accepted into CLEAN | Quarantined / review | Failed / pending |
|---|---:|---:|---:|---:|---:|
| 1. HF JSON | 1 file, 16,098 rows | 16,098 rows | 14,041 unique IDs | 2,045 out of scope (cheat/cheatsheets), 12 duplicate rows, 6 kept flagged | 0 |
| 2. CDX indices | 3 queries | views 15,243 lines (14,806 IDs); tag 2,966 + 6,546 lines (2,944 tag IDs) | n/a (index only) | n/a | 0 |
| 3. Wayback-only command pages | 952 IDs in set difference (refreshed) | 21 pages saved and parsed (25 view parses incl. samples, all OK) | 21 | 0 | 931 pending |
| 4. Tag listing pages | 3,865 tag listing jobs planned | 52 fetched + 1 sample = 53 attempted, 49 parsed OK | 1,284 unique pairs / 299 commands | 4 pages with no command blocks quarantined; 0 redirect or ID mismatches | 3,813 pending; 3 pages need pagination (tags 101 `size` 62, 102 `sort` 176, 104 `perl` 190; 25 on page 1) |
| 5a. tg123 YAML | 11,615 files | 11,615 parsed | 304 new IDs (9,553 matched existing code) | 1,302 spam quarantined, 328 review (64 possible spam, 264 not shell-like), 1 duplicate ID | 0 |
| 5b. flatcap HTML | 569 files | 569 parsed | 1 new ID (562 matched existing code) | 4 with no command | 0 |
| 5c. yedeying | 1 tarball | CSS extracted | data.js kept raw, not merged (no verifiable IDs) | — | — |
| 6. Assets | local repos | 6 asset files | n/a | n/a | 44 referenced Wayback asset URLs not fetched |

Wayback HTTP totals: 73 successful fetches logged (`raw/wayback_html/fetch_log.tsv`) plus 5 earlier samples. 16 failures are logged in `fetch_fail.tsv`, and 6 port-80 failures in `fetch_fail_round1_port80.tsv`. Both port-443 rounds were killed after refusals; no partial files were kept.

## Clean corpus composition
| Sources contributing | Commands |
|---|---:|
| hf + tg123 | 8,988 |
| hf only | 4,218 |
| hf + tg123 + flatcap | 471 |
| tg123 only | 291 |
| hf + wayback tag listing + tg123 | 191 |
| hf + wayback tag listing | 90 |
| hf + flatcap | 62 |
| wayback view + tg123 | 15 |
| hf + wayback tag listing + tg123 + flatcap | 14 |
| tg123 + flatcap | 13 |
| wayback view only | 6 |
| other combinations | 8 |
| **Total** | **14,367** |

Descriptions: 10,054 commands have an original description, and 4,002 have only AI-generated text. AI text is stored in `description_ai` and never in `description_original`. `description_original_source` says where the original text came from: HF non-AI text (10,039) or a Wayback capture (15, recorded as `wayback_view@<timestamp>`). tg123 summaries are Chinese translations, so they are never used as original descriptions.

## Validation performed
- **URL ID vs extracted ID:** every Wayback page and every flatcap file was checked against the ID in its URL or filename. For tag pages, the effective URL had to contain `/commands/tagged/<id>` with the expected ID. There were 0 mismatches and 0 redirects among the parsed tag pages.
- **Error, redirect and soft-200 checks:** pages without a command block (soft-200 or error) are quarantined. The 4 flatcap files with no command were quarantined.
- **Required content:** every clean record has an ID and a non-empty code field.
- **Escaping and newlines:** HTML entities are decoded once. 17 records still contain entity-like residue and are flagged with `html_entity_residue`; this may be literal text in the original. 2 records contain multi-line code (`has_newline_in_code`).
- **Duplicates:** 12 HF duplicate rows and 1 tg123 duplicate ID were deduplicated and logged.
- **Conflicts:** 142 cross-source disagreements are kept in `clean/conflicts.jsonl` and were not silently overwritten. They break down as 129 code differences, 11 vote differences over time (temporal) and 2 author differences. The earlier title conflict (ID 13) was a parser defect and disappeared with the title fix. HF is the primary value; the alternative value and its source are recorded.
- **Authors, votes, dates:** taken only from a source field. Fields with no source value are null. Nothing was fabricated, and HF dates are the uploader's estimates.
- **Titles (rev 2):** on 2009-layout view pages, `<h1>` is the site banner, so 17 commands (IDs 1, 5, 12, 20, 24–26, 28, 30, 32, 35, 43, 51, 54–56, 58) were titled "Command-line-fuAlpha". The parser now reads `h2#terminal-summary` and ignores the banner `<h1>`. All 17 titles were re-extracted from our own captures; no title still contains the banner.
- **Tag foreign keys:** all 2,010 association rows reference an existing tag and an existing clean command. SQLite `foreign_key_check` shows 0 violations, and `integrity_check` returned ok.
- **Pagination identity:** each listing records `listing_total` from the "Commands tagged X (N)" header. Listings with more than one page are marked incomplete, never complete.

## Tag semantics
- `tag_status = "observed_full_block"` (299): the command's own per-command Tags block was captured. These are original tag IDs and slugs, with `evidence_kind` `per_command_tags_block` or `per_command_tags_block_html_comment` (2016+ layout, where the block is inside an HTML comment). `listed_on_tag_page` rows are also included.
- `tag_status = "unknown"` (14,068): no per-command tag evidence was acquired. This is not the same as "no tags".
- Sitewide "Top Tags", `/commands/using/` words and meta keywords are **never** used as associations.
- 2,949 tags are in the taxonomy (2,944 from CDX tag URLs plus 5 seen in per-command blocks). 1,478 of them have a display name (from anchor text); the rest have only ID and slug.

## Spam and exclusion policy
- STRONG rules (luxury-brand, replica, outlet, dress, price-pattern terms and similar) quarantine an item, with `disposition = quarantined_spam_raw_preserved`.
- A WEAK-only hit (for example cheap, sale, discount, watch, or a single price) sends the item to review (`review_not_in_clean`) when it is a tg123-only item.
- For HF items, a weak hit means `review_kept_in_clean_flagged`. There are 6 such items (IDs 3562, 5085, 5737, 8478, 9495, 10218); they look like false positives and stay in CLEAN with a review flag.
- A tg123-only item must also have shell-like code, otherwise it goes to review.
- Every rule hit is listed in the `reason` field.
- Exclusion totals by disposition: 2,045 out of scope, 1,302 spam quarantined, 328 review not in clean, 13 deduplicated, 6 review kept flagged, 8 quarantined (4 flatcap files with no command, 4 tag pages with no command blocks). Total: 3,702.
- Exclusions from the third-party layer are logged separately in `thirdparty/grok/excluded.jsonl`.

## Remaining gaps (resumable)
1. 931 Wayback-only command pages are not fetched. Their IDs are in `manifests/wayback_only_ids.tsv` and their jobs in `wayback_pending_jobs.tsv`.
2. 3,813 tag-listing pages are not fetched, including offset/pagination pages. Verified tag coverage will stay about 2% until these are fetched.
3. Tags 101 (`size`), 102 (`sort`) and 104 (`perl`) still need their later listing pages.
4. 44 Wayback asset URLs (CSS/JS/images, `/css/browser_reset.css` etc.) are not fetched.
5. 187 HF IDs have no Wayback capture, so their original text cannot be cross-verified.
6. Comments were not acquired.
7. Not checked: archive.today, Common Crawl, GitLab.
8. 304 commands have no title and 305 no author (mostly tg123-only additions, a source that lacks these fields). Of the 952 Wayback-only IDs, 132 are still in neither `clean/` nor the third-party layer.

To resume when Wayback is reachable, run from the bundle root:
`cut -f1,2 manifests/wayback_pending_jobs.tsv | tr '\t' '\n' | xargs -d '\n' -n2 -P3 tools/wayback_fetch.sh && python3 tools/process.py && python3 tools/grok/build_grok_layer.py`

## Third-party GROK layer (`thirdparty/grok/`, unverified)
- **Source:** `raw/grok/commandlinefu-mirror-site.tar.xz` (sha256 `1a20b214…a548`), a static site generated by a third party with Grok from a `commands.sqlite` that was not supplied, and with no raw captures. All 14,953 command pages were parsed read-only. AI descriptions and inferred "derived" tags on those pages were not extracted.
- **Usable parts kept:**
  - 582 commands missing from `clean/` that pass our spam rules (93 spam and 6 review rejected). 63 of them have a null title because the site's title was a "Comments (N)" heading.
  - 113 original descriptions, each for a `clean/` command with none and identical code.
  - 17,921 tag pairs on 6,287 commands: 1,077 confirmed by our evidence and 16,844 unverified.
- **Rejected tag pairs:** 975 truncated slugs, 81 slugs not in the taxonomy, and 26 that contradict a tag block we captured.
- **Measured reliability:** 88% of our 1,284 verified pairs are present on the site; the full tag set matches for 85% of the 299 fully observed commands.
- **Labelling:** every record carries `layer = "third_party_unverified"`. `clean/`, `clean/commandlinefu.sqlite` and `tag_status` are not affected by the layer. Rebuild it with `python3 tools/grok/build_grok_layer.py` after `tools/process.py`.

## Licences and safety
HF is CC0 according to its card, tg123 is under the Unlicense, and flatcap and yedeying state no licence. The content was submitted by the community; keep author attribution and a credit to commandlinefu.com. **Do not run commands from this archive without reading them first.** Some are destructive, and quarantined items may contain spam links.
