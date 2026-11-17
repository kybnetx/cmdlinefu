#!/bin/bash
# $1 relpath  $2 url (https Wayback, id_ raw capture). Bounded retries; 404 is final.
B=/home/ubuntu/clf_archive/raw/wayback_html
o="$B/$1"; [ -s "$o" ] && exit 0
r=""
for a in 1 2 3; do
  r=$(curl -sSL -m 60 -A "clf-archive-recovery/1.0 (personal preservation; polite)" -o "$o.part" -w '%{http_code} %{url_effective}' "$2" 2>/dev/null)
  code=${r%% *}
  if [ "$code" = "200" ] && [ -s "$o.part" ]; then mv "$o.part" "$o"; printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$r" "$a" >> $B/fetch_log.tsv; sleep 1; exit 0; fi
  if [ "$code" = "404" ]; then break; fi
  if [ "$code" = "429" ]; then sleep 60; else sleep $((a*5)); fi
done
rm -f "$o.part"; printf '%s\t%s\t%s\tFAIL\n' "$1" "$2" "$r" >> $B/fetch_fail.tsv
