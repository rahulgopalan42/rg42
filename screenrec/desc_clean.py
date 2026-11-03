"""Strip filler the description writers sometimes appended: facts already in other columns (HQ, Crunchbase tags,
funding total/date) and quotes of the cut-off Crunchbase line. Genuine company text is kept as written."""
import re
PATTERNS = [
    r"\s*Crunchbase's own summary reads:.*?\(text cut short in the source\)\.",
    r"\s*Headquarters: [^.]+\.",
    r"\s*Crunchbase (?:sector |industry )?tags (?:include|are)\b.*?(?=(?:\s+Total funding|\s+Crunchbase|\s+Latest funding|$))",
    r"\s*Total funding (?:is )?shown (?:is |as )?[^.]*?(?:\d{4}|\d)\.(?:\s|$)",
    r"\s*(?:The )?Latest funding (?:is )?dated [^.]*\d{4}\.",
    r"\s*(?:The |These )?(?:funding )?figures (?:here |shown )?come from Crunchbase and may be out of date\.",
    r"\s*Funding (?:figures|data) (?:come|comes|are taken) from Crunchbase[^.]*\.",
    r"\s*It is a modest-sized player whose marketing budget is limited[^.]*\.",
    r"\s*Such a company is unlikely to have a large marketing budget without further verification\.",
    r"\s*It appeared in a search for listed \(public\) companies\.",
    r"\s*Crunchbase gives its headquarters country as [^;.]*;[^.]*\.",
]
_RX = [re.compile(p, re.I | re.S) for p in PATTERNS]
def clean_about(t):
    t = str(t or '')
    for rx in _RX: t = rx.sub(' ', t)
    return re.sub(r'\s{2,}', ' ', t).strip()
