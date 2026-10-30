# Clay pull for industries never searched before (Wave 15 gap fill)

These Clay industries were left out of every earlier search. Today is 14 October 2026. The user has asked for this.
Follow /home/user/rg42/wave15/clay_slice_brief.md (tools, size slicing, TSV format, room-saving, progress file) with
these differences:
- Industries: your group key in /home/user/rg42/wave15/sector_groups.json. Some values are guesses: if Clay rejects
  a value, drop it, retry, and list dropped values in your report.
- Bands, in this order:
  AB = annual_revenue in ("1B-10B","10B-100B","100B-1T")  (one search per size bucket only if it passes 190 pages)
  C1 = annual_revenue in ("200M-500M","500M-1B")  (one search per size bucket, as in the slice brief)
  C2 = annual_revenue = "75M-200M"  (one search per size bucket, cap 100 pages each)
- Output: /home/user/rg42/wave15/clay_extra_<group>.tsv ; search field = "<band>|<size>".
- Progress file if you run low: /home/user/rg42/wave15/clay_extra_<group>.progress.txt
