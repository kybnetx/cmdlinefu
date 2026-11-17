> **Note (rev 2, 2026-11-17):** this is the original review text. The counts that are actually used are in `layer_stats.json` and `README.md` in this folder. After the rebuild, ID 98 comes from our own capture, the 17 "Command-line-fuAlpha" titles are fixed in `clean/`, and the tag check now uses 1,284 verified pairs. The "271 still missing" figure at the end did not count the 239 Wayback-only IDs that `clean/` already gets from tg123, flatcap or our own captures. The real number not in `clean/` or this layer is **132**.

# GROK archive review (`commandlinefu-mirror-site.tar.xz`), 2026-11-17

## What the file is
- It is a **generated static website**: an Apache site with `generate.py`, `install.sh`/`uninstall.sh` and 42,086 HTML pages, 302 MB unpacked. The tarball is 7,897,452 bytes, `xz -t` passes, and its sha256 is `1a20b214014688fbe5550984721c64747370957f0ce8803ca593f2950c22a548`.
- It contains **no raw captures and no database**. `README-SITE.md` says it was built from `commands.sqlite`, but that file is not included.
- I recovered the data by parsing all 14,953 command pages (0 parse failures). Nothing was executed or installed.
- Safety: the archive has no symlinks, no absolute paths and no `../` paths.

## What it adds
| Item | Count | Status |
|---|---:|---|
| Commands missing from our clean corpus | 682 | 681 are in our Wayback-only gap list, which has 952 IDs |
| …flagged by our spam rules | 93 spam + 6 review | GROK left these on the site |
| …usable after spam removal | 583 | only 1 can be checked against our raw captures |
| …with a wrong title ("Comments (N)") | 64 | title set to empty; the URL slug is kept instead |
| Original descriptions where we have none | 114 | all came from Wayback view pages |
| Tag pairs marked "original" | 19,003 on 6,296 commands | see the tag check below |
| AI-written descriptions | 4,002 | kept separate in a labelled box (correct) |
| "Derived" tags (guessed from command text) | 16,785 chips | **not usable**; tags must never be inferred |

## Accuracy checks against our raw evidence
- **Code:** 17 of 17 matches on the Wayback command pages we hold. The author name appears on the page in all 17.
- **Titles:** 12 of those 17 are wrong. GROK's parser took the "Comments (N)" heading from 2009 pages. Across the whole site, 88 titles have this problem.
- **Tags, compared with our 642 confirmed pairs:** 594 agree. The 48 missing are mostly newer commands (ID 14000 and up) where GROK has no tags.
- **Tags, out-of-sample check** against 35 tag pages fetched tonight that are not yet in our tables:
  - 160 of 183 listed pairs are present in GROK;
  - 122 of 161 complete tag sets match exactly;
  - GROK has no tags at all for 21 commands that do have tags;
  - 17 commands have extra tags, most of them truncated.
- **Junk tags:** 975 pairs (5%, on 839 commands) are truncated slugs such as `p`, `co`, `di` or `date-ma`. They match GROK's stub pages, such as `/commands/tagged/675/co/`. Likely cause: truncated Wayback URLs were treated as tags. Another 81 slugs are not in our 2,948-tag taxonomy. All of these are rejected.

## Defects in our own corpus that this review exposed
- 17 titles read "Command-line-fuAlpha". Our parser read the 2009 header instead of `<title>`. This is fixable from our raw captures.
- 304 commands have no title and 305 no author. Most are additions from tg123, a source that lacks those fields.

## Supplement files (separate from the verified corpus; nothing merged)
- `grok_gap_commands.jsonl`: the 682 missing commands, each with a spam verdict, code check and title flag.
- `grok_description_supplement.jsonl`: the 114 original descriptions.
- `grok_tag_pairs.csv`: all 19,003 pairs, each classified. Counts by status:
  - `unverified_third_party`: 17,378
  - `confirmed_by_our_evidence`: 556
  - `not_in_our_observed_full_block`: 13
  - `rejected_truncated_slug`: 975
  - `rejected_slug_not_in_taxonomy`: 81

  Usable pairs cover 6,287 commands, 6,237 of them in our clean corpus.
- `supplement_stats.json`: the exact counts.

## Remaining gap after GROK
- 271 Wayback-only IDs are still missing (952 − 681).
- GROK's tags have no raw evidence behind them. In the checks above they are right about 87–92% of the time, so they must stay labelled third-party/unverified until checked against Wayback captures.
