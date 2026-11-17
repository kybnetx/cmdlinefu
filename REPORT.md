# commandlinefu.com archive bundle: acquisition and verification report

Retrieval date: 2026-11-17. Scope: archival data and asset recovery only. Nothing was built or deployed, and no archived shell command was executed.

## Bottom line
- The CLEAN corpus has **14,364 commands** keyed by original commandlinefu ID. They come from Hugging Face (base), tg123 YAML, flatcap HTML and Wayback captures.
- **Coverage is partial.** The Wayback Machine refused connections from the acquisition VM on 2026-11-17, first on port 80 and then on port 443. Per the two-failure rule, that route was stopped. **4,782 Wayback fetch jobs remain pending** (3,848 tag-listing pages and 934 Wayback-only command pages). They are resumable with `tools/wayback_fetch.sh`.
- **Original tags are recovered for 143 commands (about 1.0%)**: 642 unique command-tag pairs across 239 tags, all with capture provenance. The other 14,221 commands have `tag_status = "unknown"`, which means not recovered. It does not mean the command had no tags. No tags were inferred.
- 3,698 records are logged in `manifests/exclusions.jsonl`. These are spam, review items, duplicates and out-of-scope rows. All raw evidence is kept under `raw/`.
- This bundle is not claimed to be error-free or complete. The counts below are exact for what was acquired.

## Layout
| Path | Contents |
|---|---|
| `raw/` | Immutable acquisitions: HF JSON, CDX indices, Wayback HTML plus fetch logs, tg123 repo and tarball, flatcap tarball plus extract, yedeying tarball |
| `clean/commands.jsonl` | Clean deduplicated corpus, one JSON object per command |
| `clean/tags.csv` | Tag taxonomy: original tag_id, slug, name, evidence |
| `clean/command_tags.csv` | Association evidence rows (1,037 rows = 642 unique pairs) with capture timestamp, URL and raw file |
| `clean/conflicts.jsonl` | Cross-source disagreements (139) |
| `clean/commandlinefu.sqlite` | Same data in tables tags, commands, command_tags, conflicts, exclusions (FKs enforced) |
| `manifests/sources.json` | Source URLs, licence, retrieval date, sha256, counts |
| `manifests/exclusions.jsonl` | Quarantine/exclusion log: source, key, reason, disposition, detail, raw_path |
| `manifests/processing_stats.json` | Machine-readable counts from the last processing run |
| `manifests/wayback_pending_jobs.tsv` | 4,782 unfetched Wayback jobs (resumable) |
| `manifests/wayback_only_ids.tsv` | 952 command IDs with Wayback captures that are absent from HF |
| `manifests/tag_pages_parsed.json` | Per-tag-page parse results (listing totals, effective URL, pagination state) |
| `manifests/asset_urls_todo.txt` | 44 CSS/JS/image URLs referenced by the archived pages, not yet fetched |
| `manifests/SHA256SUMS` | Checksums of every file in the bundle except itself |
| `assets/` | Recovered static assets: flatcap `style.css`, yedeying `css/bootstrap.css` and `css/style.css`, tg123 `wwwroot` (site.css, site.js, favicon.ico) |
| `tools/process.py`, `tools/wayback_fetch.sh` | Processing pipeline and resumable fetcher. Neither one executes archived commands |

## Acquisition counts by step (recommended order)
| Step | Attempted | Downloaded / parsed | Accepted into CLEAN | Quarantined / review | Failed / pending |
|---|---:|---:|---:|---:|---:|
| 1. HF JSON | 1 file, 16,098 rows | 16,098 rows | 14,041 unique IDs | 2,045 out of scope (cheat/cheatsheets), 12 duplicate rows, 6 kept flagged | 0 |
| 2. CDX indices | 3 queries | views 15,243 lines (14,806 IDs); tag 2,966 + 6,546 lines (2,944 tag IDs) | n/a (index only) | n/a | 0 |
| 3. Wayback-only command pages | 952 IDs in set difference (refreshed) | 18 pages saved and parsed (22 view parses incl. samples, all OK) | 18 | 0 | 934 pending |
| 4. Tag listing pages | 3,865 tag listing jobs planned | 17 fetched + 1 sample = 18 parsed OK | 642 unique pairs / 143 commands | 0 redirect or ID mismatches | 3,848 pending; 1 page needs pagination (tag 101 `size`: 62 listed, 25 on page 1) |
| 5a. tg123 YAML | 11,615 files | 11,615 parsed | 304 new IDs (9,553 matched existing code) | 1,302 spam quarantined, 328 review (64 possible spam, 264 not shell-like), 1 duplicate ID | 0 |
| 5b. flatcap HTML | 569 files | 569 parsed | 1 new ID (562 matched existing code) | 4 with no command | 0 |
| 5c. yedeying | 1 tarball | CSS extracted | data.js kept raw, not merged (no verifiable IDs) | — | — |
| 6. Assets | local repos | 6 asset files | n/a | n/a | 44 referenced Wayback asset URLs not fetched |

Wayback HTTP totals: 35 successful fetches logged (`raw/wayback_html/fetch_log.tsv`) plus 5 earlier samples. There were 6 logged port-80 connection failures. The port-443 round was killed after refusals; no partial files were kept.

## Clean corpus composition
| Sources contributing | Commands |
|---|---:|
| hf + tg123 | 9,086 |
| hf only | 4,262 |
| hf + tg123 + flatcap | 482 |
| tg123 only | 291 |
| hf + wayback tag listing + tg123 | 93 |
| hf + flatcap | 65 |
| hf + wayback tag listing | 46 |
| wayback view + tg123 | 15 |
| tg123 + flatcap | 13 |
| wayback view only | 3 |
| other combinations | 8 |
| **Total** | **14,364** |

Descriptions: 10,052 commands have an original description, and 4,002 have only AI-generated text. AI text is stored in `description_ai` and never in `description_original`. `description_original_source` says where the original text came from: HF non-AI text (10,039) or a Wayback capture (13, recorded as `wayback_view@<timestamp>`). tg123 summaries are Chinese translations, so they are never used as original descriptions.

## Validation performed
- **URL ID vs extracted ID:** every Wayback page and every flatcap file was checked against the ID in its URL or filename. For tag pages, the effective URL had to contain `/commands/tagged/<id>` with the expected ID. There were 0 mismatches and 0 redirects among the parsed tag pages.
- **Error, redirect and soft-200 checks:** pages without a command block (soft-200 or error) are quarantined. The 4 flatcap files with no command were quarantined.
- **Required content:** every clean record has an ID and a non-empty code field.
- **Escaping and newlines:** HTML entities are decoded once. 17 records still contain entity-like residue and are flagged with `html_entity_residue`; this may be literal text in the original. 2 records contain multi-line code (`has_newline_in_code`).
- **Duplicates:** 12 HF duplicate rows and 1 tg123 duplicate ID were deduplicated and logged.
- **Conflicts:** 139 cross-source disagreements are kept in `clean/conflicts.jsonl` and were not silently overwritten. They break down as 129 code differences, 7 vote differences over time (temporal), 2 author differences and 1 title difference. HF is the primary value; the alternative value and its source are recorded.
- **Authors, votes, dates:** taken only from a source field. Fields with no source value are null. Nothing was fabricated, and HF dates are the uploader's estimates.
- **Tag foreign keys:** all 1,037 association rows reference an existing tag and an existing clean command. SQLite `foreign_key_check` shows 0 violations, and `integrity_check` returned ok.
- **Pagination identity:** each listing records `listing_total` from the "Commands tagged X (N)" header. Listings with more than one page are marked incomplete, never complete.

## Tag semantics
- `tag_status = "observed_full_block"` (143): the command's own per-command Tags block was captured. These are original tag IDs and slugs, with `evidence_kind` `per_command_tags_block` or `per_command_tags_block_html_comment` (2016+ layout, where the block is inside an HTML comment). `listed_on_tag_page` rows are also included.
- `tag_status = "unknown"` (14,221): no per-command tag evidence was acquired. This is not the same as "no tags".
- Sitewide "Top Tags", `/commands/using/` words and meta keywords are **never** used as associations.
- 2,948 tags are in the taxonomy (2,944 from CDX tag URLs plus 4 seen in per-command blocks). 1,440 of them have a display name (from anchor text); the rest have only ID and slug.

## Spam and exclusion policy
- STRONG rules (luxury-brand, replica, outlet, dress, price-pattern terms and similar) quarantine an item, with `disposition = quarantined_spam_raw_preserved`.
- A WEAK-only hit (for example cheap, sale, discount, watch, or a single price) sends the item to review (`review_not_in_clean`) when it is a tg123-only item.
- For HF items, a weak hit means `review_kept_in_clean_flagged`. There are 6 such items (IDs 3562, 5085, 5737, 8478, 9495, 10218); they look like false positives and stay in CLEAN with a review flag.
- A tg123-only item must also have shell-like code, otherwise it goes to review.
- Every rule hit is listed in the `reason` field.
- Exclusion totals by disposition: 2,045 out of scope, 1,302 spam quarantined, 328 review not in clean, 13 deduplicated, 6 review kept flagged, 4 quarantined (no command). Total: 3,698.

## Remaining gaps (resumable)
1. 934 Wayback-only command pages are not fetched. Their IDs are in `manifests/wayback_only_ids.tsv` and their jobs in `wayback_pending_jobs.tsv`.
2. 3,848 tag-listing pages are not fetched, including offset/pagination pages. Tag coverage will stay about 1% until these are fetched.
3. Tag 101 (`size`) still needs pages 2 and 3.
4. 44 Wayback asset URLs (CSS/JS/images, `/css/browser_reset.css` etc.) are not fetched.
5. 187 HF IDs have no Wayback capture, so their original text cannot be cross-verified.
6. Comments were not acquired.
7. Not checked: archive.today, Common Crawl, GitLab.

To resume when Wayback is reachable, run from the bundle root:
`cut -f1,2 manifests/wayback_pending_jobs.tsv | tr '\t' '\n' | xargs -d '\n' -n2 -P3 tools/wayback_fetch.sh && python3 tools/process.py`

## Licences and safety
HF is CC0 according to its card, tg123 is under the Unlicense, and flatcap and yedeying state no licence. The content was submitted by the community; keep author attribution and a credit to commandlinefu.com. **Do not run commands from this archive without reading them first.** Some are destructive, and quarantined items may contain spam links.
