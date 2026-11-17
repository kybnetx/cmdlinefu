# cmdlinefu: archived mirror of commandlinefu.com

This repository is a **data archive** of [commandlinefu.com](https://www.commandlinefu.com), the community site of shell one-liners. It was assembled on **2026-11-17** from public secondary sources: a Hugging Face dataset, Wayback Machine CDX indices and captures, and community GitHub mirrors. Every raw acquisition is kept next to a cleaned, deduplicated corpus. Checksums cover all of it.

It is not a website and nothing here is deployed. The full acquisition and verification report is in [`REPORT.md`](REPORT.md), and the source research is in [`docs/commandlinefu-archive-sources.md`](docs/commandlinefu-archive-sources.md).

> ⚠️ **Do not run commands from this archive blindly.** These are user-submitted shell commands. Some are destructive (`rm`, `dd`, `mkfs`, fork bombs, `chmod -R` …), some depend on a specific system, and quarantined items under `raw/` may contain spam links. Read and understand a command before you run it. The tooling in this repo never executes archived commands.

## Key counts

| Item | Count |
|---|---:|
| Clean commands, keyed by original commandlinefu ID | **14,364** |
| Commands with an original description | 10,052 |
| Commands with only an AI-written description (stored separately in `description_ai`) | 4,002 |
| Tags in the taxonomy (of which 1,440 have a display name) | 2,948 |
| Unique command–tag pairs recovered | 642, covering **143 commands (~1.0%)** |
| Exclusions logged (`manifests/exclusions.jsonl`) | 3,698 |
| Cross-source conflicts kept (`clean/conflicts.jsonl`) | 139 (129 code, 7 votes, 2 author, 1 title) |
| Wayback fetch jobs still pending | 4,782 |
| Files covered by `manifests/SHA256SUMS` | 12,335 |

## Layout

| Path | Contents |
|---|---|
| `raw/` | Immutable acquisitions: HF JSON, Wayback CDX indices, Wayback HTML plus fetch logs, tg123 repo and tarball, flatcap tarball plus extract, yedeying tarball. Quarantined spam is kept here as raw evidence |
| `clean/commands.jsonl` | Clean deduplicated corpus, one JSON object per command |
| `clean/tags.csv`, `clean/command_tags.csv` | Tag taxonomy, and command–tag association evidence with capture provenance |
| `clean/conflicts.jsonl` | Cross-source disagreements. They are recorded, not silently overwritten |
| `clean/commandlinefu.sqlite` | The same data as SQLite tables: `tags`, `commands`, `command_tags`, `conflicts`, `exclusions` |
| `manifests/` | `sources.json` (URLs, licences, sha256, counts), `exclusions.jsonl`, `processing_stats.json`, `wayback_pending_jobs.tsv`, `wayback_only_ids.tsv`, `tag_pages_parsed.json`, `asset_urls_todo.txt`, `SHA256SUMS` |
| `assets/` | Recovered static assets (CSS/JS/favicon) from the community mirrors |
| `tools/` | `process.py` (processing pipeline) and `wayback_fetch.sh` (resumable Wayback fetcher) |
| `REPORT.md` | Acquisition and verification report |
| `docs/` | Source research notes |

## Verify integrity

From the repository root:

```sh
sha256sum -c manifests/SHA256SUMS
```

Every line should end in `OK`. `SHA256SUMS` covers the archive tree (`raw/`, `clean/`, `manifests/`, `assets/`, `tools/`, `REPORT.md`). It does **not** cover the repo-level files added for publishing (`README.md`, `.gitattributes`, `docs/`). `.gitattributes` turns off end-of-line conversion for the archived files so that checksums still verify on any platform.

## Limitations (please read)

- **Tags are mostly unknown.** Original tags were recovered for only 143 commands (about 1.0%). The other 14,221 commands have `tag_status = "unknown"`. That means the tags were *not recovered*, **not** that the command had no tags. No tags were inferred.
- **Coverage is partial.** The Wayback Machine was unreachable from the acquisition machine, so **4,782 Wayback jobs are pending**: 3,848 tag-listing pages and 934 Wayback-only command pages. They can be resumed with `tools/wayback_fetch.sh` over `manifests/wayback_pending_jobs.tsv` (see `REPORT.md` → *Remaining gaps*). 44 referenced asset URLs were also not fetched, and comments were not acquired.
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

No licence for the original commandlinefu.com content itself is recorded in this archive, and this repository does not grant one. Treat it as an archival/research copy.
