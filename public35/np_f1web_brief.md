# Addendum to f1web_brief.md (new-parameters run, 19 Nov 2026)

Read f1web_brief.md first: it defines the job (one WebSearch per company to check whether it is a current Formula 1
sponsor) and the output fields sym, status, detail, source_url. Two changes for this run:

1. Each input line also carries `signals`: buying signals written from desk research that have NOT been checked.
   If `signals` is not empty, run ONE more WebSearch on the most concrete item in it (an IPO, a funding round, a new
   CEO, an acquisition, a rebrand, a new sponsorship) and add two fields to your output line:
     "signal_status": "confirmed" | "not found" | "contradicted",
     "signal_note": "what the results show, under 30 words, with the date",
     "signal_url": "a URL from your search results that supports it, or \"\""
   If `signals` is empty, write "signal_status": "", "signal_note": "", "signal_url": "".
   Judge only from what the search results show. "contradicted" = the results show the event did not happen, or
   happened differently (say how).

2. Search budget: at most 2 searches per company and never more than the total given in your instructions. If you
   run out, mark the rest "not_checked" (and signal_status "") and finish.
