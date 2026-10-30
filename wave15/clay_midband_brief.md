# Clay mid-band pull brief (Wave 15, USD 150M-1B revenue)

Same as clay_pull_brief.md, except replace the A/B searches with these two (Clay bucket names are exact):

C1. select from companies where industry in (<your industries>) and annual_revenue in ("200M-500M", "500M-1B")
    Page to the end (cap 400 pages). Write search = "C1".
C2. select from companies where industry in (<your industries>) and annual_revenue = "75M-200M"
    Page to the end (cap 100 pages). Write search = "C2".

Output: /home/user/rg42/wave15/clay_mid_<group>.tsv. Run C1 first. If Clay says too many concurrent requests, wait
briefly and retry. The USD 150M floor is applied later at triage.
