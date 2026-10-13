# Clay mid-band pull brief (Wave 15, USD 150M-1B revenue)

Same as clay_pull_brief.md, except run ONE search per group instead of A/B:

C. select from companies where industry in (<your industries>) and annual_revenue in (<the Clay revenue buckets covering 100M up to 1B>)

Use the bucket values Clay accepts (try "100M-250M", "250M-500M", "500M-1B"; if Clay rejects a value, use the valid values its error lists). Page to the end (cap 200 pages). Write search = "C". Output: /home/user/rg42/wave15/clay_mid_<group>.tsv. Revenue floor of USD 150M is applied later at triage; companies in a 100M-250M bucket are kept for checking.
