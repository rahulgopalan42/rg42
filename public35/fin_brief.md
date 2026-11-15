# Brief: latest-year financial figures from stockanalysis.com for listed companies

Each input line is a listed company (JSON: sym, name, country, url_guess). Open the company's income-statement page on
stockanalysis.com with WebFetch (one page per company) and read the figures for the LATEST COMPLETE FISCAL YEAR
(the most recent annual column, not TTM). `url_guess` is our best guess at the page; if it 404s, try once more with the
obvious alternative (US-listed: https://stockanalysis.com/stocks/<ticker>/financials/ ; others:
https://stockanalysis.com/quote/<exchange code>/<ticker>/financials/ with codes such as tyo, hkg, sha, she, krx, epa,
lon, etr, fra, bit, swx, tpe, bme, asx, sto, bkk, cph, ams, sgx, bvmf, tsx, bmv, klse, tadawul, adx, dfm, nse, jse,
hel, vie, ist, qse, wse, idx). Then move on. No WebSearch.

Ask the page for exactly these rows of the latest fiscal-year column: fiscal year label and period end date, reporting
currency, Revenue, Revenue Growth (YoY) %, Operating Income, EBITDA, Free Cash Flow, and "Advertising Expenses" /
"Selling & Marketing" if the page has such a row. Values are usually in millions of the reporting currency.

Write one JSON object per input line, same order, to the output file (append every 10 companies so progress is saved):
{"sym": "...", "found": true, "fy": "FY2025", "period_end": "2025-12-31", "currency": "JPY", "unit": "millions",
 "revenue": 12345.6, "revenue_growth_pct": 7.4, "operating_income": 1234.5, "ebitda": 2345.6, "free_cash_flow": 987.6,
 "advertising": null, "selling_marketing": null, "source_url": "https://stockanalysis.com/..."}
Use null for anything the page does not show. Numbers exactly as shown on the page (no conversion, no estimates,
negative numbers negative). If the page cannot be opened or shows no annual figures: {"sym": "...", "found": false}.
Never fill a number from memory. Keep helper files in your own scratch directory (named in your instructions). Create
no other files in the repository. Reply with: found / not found counts and anything odd.
