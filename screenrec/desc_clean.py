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

# stock closing lines one writer appended from a fixed pool (generic, and the ownership ones may not fit the row)
STOCK = ["Business-to-business model, so brand exposure through a consumer sport would be of limited commercial use.",
         "Sells to professional buyers rather than the public, so sport sponsorship would reach few of its customers.",
         "Its buyers are specialist or industrial professionals, so the fit with a mass-audience sport is limited.",
         "Income depends on trial milestones and partner payments rather than product sales, which limits sponsorship budgets.",
         "No marketed product yet, so spending on consumer brand-building is unlikely.",
         "Pre-revenue and funded by investors, so marketing budgets are minimal and sponsorship appetite is low.",
         "No longer trading as an independent business, so there is no active marketing budget to approach.",
         "Now part of a larger group, so any sponsorship decision would sit with the parent company.",
         "No longer independent, so outreach would need to go through its new owner.",
         "Ownership has changed hands, so budgets and brand decisions rest with the acquirer.",
         "Operations have ceased, so it is not a live sponsorship prospect."]
_RX = [re.compile(p, re.I | re.S) for p in PATTERNS] + [re.compile(r'\s*' + re.escape(x)) for x in STOCK]
def clean_about(t):
    t = str(t or '')
    for rx in _RX: t = rx.sub(' ', t)
    return re.sub(r'\s{2,}', ' ', t).strip()
