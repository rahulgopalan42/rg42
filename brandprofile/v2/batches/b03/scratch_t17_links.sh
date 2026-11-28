#!/bin/bash
# scratch: list about/news/leadership links on a site's homepage
for d in "$@"; do
  echo "== $d"
  curl -sL -m 20 -A "Mozilla/5.0 (compatible; research-bot)" "https://$d/" | grep -oE 'href="[^"#]*"' | sed 's/href="//;s/"$//' | grep -iE 'about|news|press|media|leader|company|who-we|history|our-story|kurumsal|unternehmen|presse|actualit|noticias|sobre|empresa|sponsor' | sort -u | head -15
done
