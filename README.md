# cmdlinefu: archived mirror of commandlinefu.com

This repository is a **data archive** of [commandlinefu.com](https://www.commandlinefu.com), the community site of shell one-liners. It was assembled on **2026-11-17** from public secondary sources: a Hugging Face dataset, Wayback Machine CDX indices and captures, and community GitHub mirrors. Data from a third-party, Grok-generated mirror site was checked against this evidence and merged into the same corpus at the lowest precedence. Every value it supplies is marked. Every raw acquisition is kept next to a cleaned, deduplicated corpus. Checksums cover all of it.

It is not a website and nothing here is deployed. The full acquisition and verification report is in [`REPORT.md`](REPORT.md), and the source research is in [`docs/commandlinefu-archive-sources.md`](docs/commandlinefu-archive-sources.md).

> ⚠️ **Do not run commands from this archive blindly.** These are user-submitted shell commands. Some are destructive (`rm`, `dd`, `mkfs`, fork bombs, `chmod -R` …), some depend on a specific system, and quarantined items under `raw/` may contain spam links. Read and understand a command before you run it. The tooling in this repo never executes archived commands.

## Key counts

| Item | Count |
|---|---:|
| Clean commands, keyed by original commandlinefu ID | **14,949** (14,367 evidence-backed + 582 `third_party_only`) |
| Commands with an original description | 10,516 (462 of them from the mirror site, `description_original_source = grok_mirror`) |
| Commands with only an AI-written description (stored separately in `description_ai`) | 4,002 |
| Tags in the taxonomy (of which 1,478 have a display name) | 2,949 |
| Command–tag pairs with own capture evidence | 1,284, covering **299 commands** |
| Command–tag pairs from the mirror site only (`third_party_unverified`) | 16,838, covering 6,017 commands |
| Exclusions logged (`manifests/exclusions.jsonl`) | 4,863 |
| Cross-source conflicts kept (`clean/conflicts.jsonl`) | 155 (132 code, 11 votes, 9 tag sets, 2 author, 1 date) |
| Wayback fetch jobs still pending | 4,744 |
| Files covered by `manifests/SHA256SUMS` | 12,378 |

## Layout

| Path | Contents |
|---|---|
| `raw/` | Immutable acquisitions: HF JSON, Wayback CDX indices, Wayback HTML plus fetch logs, tg123 repo and tarball, flatcap tarball plus extract, yedeying tarball, and the third-party Grok mirror-site tarball with its page extract (`raw/grok/`). Quarantined spam is kept here as raw evidence |
| `clean/commands.jsonl` | The unified corpus, one JSON object per command. Third-party values are marked per record by `sources` (`grok_mirror`), `third_party_fields`, `third_party_checks`, `title_issue` and `*_source` |
| `clean/tags.csv`, `clean/command_tags.csv` | Tag taxonomy, and command–tag association evidence with capture provenance |
| `clean/conflicts.jsonl` | Cross-source disagreements. They are recorded, not silently overwritten |
| `clean/commandlinefu.sqlite` | The same data as SQLite tables: `tags`, `commands`, `command_tags`, `conflicts`, `exclusions` |
| `manifests/` | `sources.json` (URLs, licences, sha256, counts), `exclusions.jsonl`, `processing_stats.json`, `wayback_pending_jobs.tsv`, `wayback_only_ids.tsv`, `tag_pages_parsed.json`, `asset_urls_todo.txt`, `SHA256SUMS` |
| `assets/` | Recovered static assets (CSS/JS/favicon) from the community mirrors |
| `tools/` | `process.py` (processing pipeline), `wayback_fetch.sh` (resumable Wayback fetcher) `grok/parse_grok.py` (read-only extractor for the third-party site) and `validate_unified.py` (merge invariant checks) |
| `REPORT.md` | Acquisition and verification report |
| `docs/` | Source research notes |

## Verify integrity

From the repository root:

```sh
sha256sum -c manifests/SHA256SUMS
```

Every line should end in `OK`. `SHA256SUMS` covers the archive tree (`raw/`, `clean/`, `manifests/`, `assets/`, `tools/`, `REPORT.md`). It does **not** cover the repo-level files added for publishing (`README.md`, `.gitattributes`, `docs/`). `.gitattributes` turns off end-of-line conversion for the archived files so that checksums still verify on any platform.

## Limitations (please read)

- **Tags are mostly unknown.** Tags with our own capture evidence exist for only 299 commands. Another 6,017 carry `tag_status = "third_party_unverified"` tags from the mirror site. The other 8,633 commands have `tag_status = "unknown"`. That means the tags were *not recovered*, **not** that the command had no tags. No tags were inferred.
- **Coverage is partial.** The Wayback Machine was unreachable from the acquisition machine, so **4,744 Wayback jobs are pending**: 3,813 tag-listing pages and 931 Wayback-only command pages. They can be resumed with `tools/wayback_fetch.sh` over `manifests/wayback_pending_jobs.tsv` (see `REPORT.md` → *Remaining gaps*). 44 referenced asset URLs were also not fetched, and comments were not acquired.
- **Third-party values are unverified.** The mirror site has no raw captures. It never overrides an evidence-backed value; `tools/validate_unified.py` checks this, and the check confirmed that none of the 14,367 pre-merge records changed. Measured against our own evidence:
  - code is identical for 14,269 of 14,272 shared IDs;
  - titles, authors and dates match in every case but one;
  - the site has 84% of our own tag pairs.

  94 of its titles were bad ("Comments (N)" or truncated) and are set to null. Show `third_party_only` records, `third_party_fields` and `third_party_unverified` tags with a visible "unverified" label. See `REPORT.md` → *Third-party merge*.
- **AI-written descriptions are kept separate.** 4,002 commands have only AI-generated text from the HF dataset. It is stored in `description_ai` and never in `description_original`.
- **Spam is quarantined, not deleted.** 1,302 spam items from the tg123 mirror were excluded from `clean/` but stay under `raw/` as evidence. Every exclusion is logged with its reason in `manifests/exclusions.jsonl`.
- Authors, votes and dates come only from source fields and are null otherwise. HF dates are the uploader's estimates. The archive is not claimed to be complete or error-free.

## Sources, licences and attribution

All content was originally submitted by the commandlinefu.com community. **Keep the author attribution and credit commandlinefu.com** when you reuse it. Licences as recorded in `manifests/sources.json` and `REPORT.md`:

| Source | URL | Licence as recorded |
|---|---|---|
| Hugging Face `b-mc2/cli-commands-explained` | https://huggingface.co/datasets/b-mc2/cli-commands-explained | CC0 (dataset card); underlying content user-submitted |
| Wayback CDX indices and captures | https://web.archive.org/ | Internet Archive terms |
| GitHub `tg123/commandlinefu.cn` | https://github.com/tg123/commandlinefu.cn | Unlicense |
| GitHub `flatcap/misc-commandlinefu` | https://github.com/flatcap/misc-commandlinefu | none stated |
| GitHub `yedeying/commandlinefu-offline` | https://github.com/yedeying/commandlinefu-offline | none stated |
| Grok-generated mirror site `commandlinefu-mirror-site.tar.xz` (third party, supplied by the repo owner) | — (sha256 `1a20b214…a548`) | none stated; merged at lowest precedence, marked `grok_mirror` |

No licence for the original commandlinefu.com content itself is recorded in this archive, and this repository does not grant one. Treat it as an archival/research copy.
