# Wave 14 TRACK F verification brief — funded USD 100M+ (rebuilt 6 Oct 2026)

Same output schema, flags, fit score, verdicts, F1-tie rules, sanctions rules, duplicate rule and search budget as W14_verify_brief.md (read it too). Differences:
- Gate 1 (replaces valuation): cumulative EQUITY funding >= USD 100M, dated and sourced. Strip debt, venture debt, credit/warehouse facilities, grants, government contracts, non-dilutive "customer value fund" money, and secondary sales where the split is disclosed. If the equity/debt split is undisclosed and the headline only just clears USD 100M, pass with flag "equity share unconfirmed" and cap at Stretch; if documented equity is clearly below USD 100M, No.
- Gate 1b (capacity): at least one PRICED equity round within the last 24 months (closing date; today is in the task). Older = No. Announcement vs close within days of the cutoff: pass and flag "at edge of 24-month window".
- Valuation is recorded but NOT required. If the valuation is USD 1B or above, add the flag "valuation above USD 1B: main-list overlap".
- Listed companies are out of Track F scope: verdict No, reason "listed; out of Track F scope".
- Companies acquired by another company = No (filter 4, acquired).
- Rights-holders (leagues, teams, venues, media producers) are Low-value unless a sponsorship-buying motive exists.
Write ALL records before stopping; if the budget runs out, write what you have and say which remain. Report tally and hard-filter failures.
