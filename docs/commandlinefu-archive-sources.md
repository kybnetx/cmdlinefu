# commandlinefu.com: recoverable archives and mirrors (research only)

Research date: 2026-11-17. Scope: source discovery, feasibility, and (update below) archive acquisition. Nothing was built or deployed.

## Bottom line
- The original site is not reachable. `commandlinefu.com` has no A record and `www` is a CNAME to the apex, so requests fail with "could not resolve host". The domain is still registered until 2027-01-20 (RDAP) and the AWS Route 53 nameservers still answer. Web-search snippets that say the site is "online in 2026" are stale. No plan below depends on the live site.
- **No complete, tag-bearing dump was found in the sources checked.** The practical corpus is the Hugging Face dataset (best structured base) plus the Wayback Machine (the only source with original tag pages, vote snapshots, layout and CSS).
- **Tags are only partly recovered (143 commands, see update).** The structured sources omit tags. The only original tag evidence is archived tag pages. See the tag section.
- No live public mirror was found. I did not check archive.today, Common Crawl or GitLab.

## Update 2026-11-17: acquisition executed (refreshed counts)
The acquisition was run in the recommended order. Results are in the project file `commandlinefu-archive-bundle-2026-11-17.tar.gz`; see `commandlinefu-acquisition-report.md` for details.
- HF: 16,098 rows, of which 14,053 are commandlinefu rows with 14,041 unique IDs.
- Wayback CDX: 14,806 command IDs with 200 captures. Refreshed set difference: 952 Wayback-only IDs and 187 HF-only IDs. Tag CDX: 2,944 tag IDs.
- tg123: 11,615 files and 10,248 valid unique IDs. 1,302 were quarantined as spam, 328 sent to review, and 304 IDs added.
- flatcap: 569 pages parsed and 1 ID added.
- Clean corpus: 14,364 commands.
- **Tags: original tags were recovered for 143 commands** (642 unique command-tag pairs, 239 tags), about 1.0%. All other commands are "unknown", not "no tags".
- **Wayback blocked:** the archive refused connections from the acquisition VM (port 80, then port 443). Of the planned jobs, 4,782 are still pending and resumable: 3,848 tag pages and 934 command pages. Only 18 Wayback-only commands and 17 tag pages were fetched before the block.

## Source comparison
| # | Source | Type | Observed coverage | Tags? | Licence / caveat |
|---|---|---|---|---|---|
| 1 | Hugging Face `b-mc2/cli-commands-explained` | Real data (JSON) | 16,098 rows. 14,053 are commandlinefu (14,041 unique IDs, 2 to 34,946, dates 2009-01-22 to 2024-03-19). 4,014 of those have AI-written descriptions (flag `ai_generated_description`). Fields: id, votes, url, title, description, code, author, date | **No** (schema has no tag field) | Card says CC0. Underlying content is user-submitted, so attribution and provenance are unclear. Cleansed and partly filtered by the uploader, and dates are labelled estimates |
| 2 | Wayback command pages `/commands/view/<id>/<slug>` | Real HTML captures | 14,806 unique command IDs with HTTP-200 captures (IDs 1 to 44,445). Captures run 2009-02-08 to 2026-10-17. Of these IDs, 13,854 overlap the Hugging Face set, 952 are not in it, and 187 Hugging Face IDs have no Wayback capture | **Not per command in the samples inspected** (see below) | Archive terms apply. Rate-limit your fetching |
| 3 | Wayback tag pages `/commands/tagged/<tagid>/<slug>` | Real HTML captures | 2,966 unique tag URLs with 200 captures (plus about 2,973 `/rss` variants). Highest tag ID seen is 5,673 | **Yes: original tag ID and slug, plus the commands listed under it** | Pagination depth not verified |
| 4 | Wayback `/commands/browse/json` | Real API output | At least one 200 capture, 2023-11-28. Served gzip-compressed | Not checked | Single 25-item page, so not a corpus |
| 5 | GitHub `tg123/commandlinefu.cn` | Real data (YAML) | 11,615 files, 11,614 unique `commandlinefu_id` values (1 to 17,189). 7,737 are marked hidden. 1,945 IDs are not in the Hugging Face set. Last commit 2017-05-21 | **No** (keys: command, summary, translator, hide, commandlinefu_id) | Unlicense for the repo. Summaries are Chinese translations. Many files are spam such as watch or jacket product names |
| 6 | GitHub `flatcap/misc-commandlinefu` | Saved HTML pages | About 578 HTML command pages plus some shell-fu text | Not verified | No licence stated. Small selection |
| 7 | GitHub `yedeying/commandlinefu-offline` | Small snapshot | `js/data.js` of about 457 KB, Chinese titles | No | No licence stated |
| 8 | About 40 GitHub client or scraper repos (for example `david-caro/Python-clfu`, `pombadev/commandlinefu`, `TheRealBarenziah/commandlinefu`, `t9md/cmdline-fu`) | Code only | No corpus | `t9md/cmdline-fu` scrapes tags from the live site (code only, no data) | Not data sources |

Exact URLs:
- https://huggingface.co/datasets/b-mc2/cli-commands-explained (file: `cli_commands_explained.json`, about 11 MB, https://huggingface.co/datasets/b-mc2/cli-commands-explained/resolve/main/cli_commands_explained.json)
- Wayback CDX, command pages: `http://web.archive.org/cdx/search/cdx?url=commandlinefu.com/commands/view/&matchType=prefix&output=txt&fl=original,timestamp&collapse=urlkey&filter=statuscode:200`
- Wayback CDX, tag pages: `http://web.archive.org/cdx/search/cdx?url=commandlinefu.com/commands/tagged/&matchType=prefix&output=txt&fl=original&collapse=urlkey&filter=statuscode:200`
- Raw page fetch pattern: `http://web.archive.org/web/<timestamp>id_/<original-url>`. Examples inspected:
  - https://web.archive.org/web/20090209223936id_/http://www.commandlinefu.com:80/commands/view/13/run-the-last-command-as-root
  - https://web.archive.org/web/20260608113841id_/https://www.commandlinefu.com/commands/view/13/run-the-last-command-as-root
  - https://web.archive.org/web/2012id_/http://www.commandlinefu.com/commands/tagged/10/date-manipulation
  - https://web.archive.org/web/20231128061322id_/https://www.commandlinefu.com/commands/browse/json
- https://github.com/tg123/commandlinefu.cn (`_data/*.yaml`)
- https://github.com/flatcap/misc-commandlinefu
- https://github.com/yedeying/commandlinefu-offline

## Original tag recovery (hard requirement)
**Status (updated): partially recovered, 143 commands; see the update above. Original text below: not recovered. Partial recovery looks feasible, but coverage is unverified.**

Confirmed observations:
1. **Hugging Face:** the schema has no tag field (id, votes, url, title, description, code, author, date, ai flag). It gives no original tags. I also did not infer or invent any.
2. **tg123 YAML:** no tag field (keys listed above). It gives no tags.
3. **Wayback command page, 2026-06-08 capture of command 13:** the only tag links are seven links in a sitewide "Top Tags" sidebar (sed, awk, find, grep, curl, bash, linux, each with its tag ID, for example `/commands/tagged/112/awk`). The same seven appear on every page, so they are **not** command 13's own tags. Treat them only as evidence that the tag ID plus slug URL scheme exists. Do not read the sidebar as command-to-tag data.
4. **Wayback command page, 2009-02-09 capture of command 13:** the sidebar links are `/commands/using/<word>` pages (a different "using" taxonomy), not tags. No per-command tag list was visible in this sample.
5. **Wayback tag page, 2012 capture of `/commands/tagged/10/date-manipulation`:** the page holds about 19 commands with their IDs, votes, descriptions and code. That confirms a command-to-tag association is recoverable from tag pages: tag ID and slug plus the commands listed under it. I saw no pagination links in the stripped HTML, so the page may show only one page of results.

Not verified:
- How many of the 2,966 tag URLs have complete command lists, and how deep the pagination goes. Heavily used tags such as `bash` and `grep` likely span many pages.
- Whether tags appear in command-page HTML from some other era. I only inspected two samples, both for command 13.
- Whether the three tag-like fields (tag list, "using" words, meta keywords) ever existed on the same page.

Best practical recovery path (not yet executed):
1. Take the 2,966 tag URLs from the tag CDX query above, plus the paginated variants and each tag's latest 200 capture.
2. Fetch each tag page (and its pages 2 and up if they exist) with `id_` raw fetches at a polite rate.
3. Parse tag ID, slug and the listed command IDs. Store the association with its Wayback timestamp as provenance.
4. Join to command IDs from Hugging Face and the 14,806-ID Wayback list.
5. Report the share of commands that end up with at least one tag, and label the rest "tags unrecovered". Do not backfill tags by guessing from command content.

Expect incomplete coverage. Older captures are 2009 to 2013, and some tags or commands may never have been archived.

## Recommended acquisition order
1. Download the Hugging Face JSON as the base corpus, keyed by original ID, and keep the AI-description flag.
2. Pull the CDX lists for command pages and tag pages, which cost little.
3. Fetch the 952 Wayback-only command IDs and extract their fields from the raw HTML.
4. Run the tag-page crawl above and measure coverage.
5. Use `tg123` to fill older IDs missing elsewhere, and exclude its spam entries.
6. Take layout, CSS and images from Wayback captures (including `/css/styles.css`) and from `flatcap`.

## Caveats and limits
- Wayback counts are unique URLs with a 200 status in the CDX index, not page-by-page checks. Some may be spam, error or redirect pages.
- Comment recovery was not assessed. Votes in Hugging Face are one snapshot per command.
- Content is community-submitted with no clear licence. Keep author attribution and a credit to commandlinefu.com on every entry.
- Archived commands were not executed.
