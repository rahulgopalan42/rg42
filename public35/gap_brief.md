# Brief: find the latest annual financial figures for listed companies that our data source does not cover

Each line of your input file is a listed company (JSON: symbol, name, country, market cap). Most are listed in the UAE
(ADX / DFM), Oman, Pakistan, Bahrain, Kuwait or Qatar. For each one find, from a page you actually open:
- latest annual (or trailing-twelve-month) REVENUE (for banks: total operating income / revenue),
- NET INCOME (or pre-tax profit) for the same period,
- CASH and equivalents if shown.
Convert to USD (state the rate you used; AED 3.6725, SAR 3.75, QAR 3.64, OMR 0.385, BHD 0.376, KWD ~0.307, PKR ~280 per USD).

How: use WebFetch on the company's stockanalysis.com page first - URL pattern https://stockanalysis.com/quote/<exchange>/<TICKER>/
(exchange codes: adx, dfm, qse, tadawul, msm, bah, kse, psx; the ticker is the symbol without its suffix), and its
/statistics/ or /financials/ sub-page. If that fails, try the company's investor-relations page or one WebSearch.
Keep WebSearch use low (you share a small search budget); skip a company after two failed attempts.

Output: JSON Lines file (path in your task), one object per input line:
{"sym": "...", "revenue_usd": number or null, "net_income_usd": number or null, "pretax_usd": number or null,
 "cash_usd": number or null, "period": "FY2025" or "TTM to 2026-09", "currency_note": "AED 12.3bn at 3.6725",
 "source_url": "page you opened", "found": true|false}
Never estimate or fill from memory: if you could not open a page with the figure, set found false and nulls.
Create no other files in the repository. Reply with: found N of M.
