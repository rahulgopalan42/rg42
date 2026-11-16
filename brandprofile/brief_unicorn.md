# Addendum for the unicorn-list check (read after brief_newsectors.md and brief_frontier.md)

Your input file holds companies taken from the Wikipedia "List of unicorn startup companies" (read 16 Nov 2026) that are NOT on the user's sheet.
Each line gives: name, wiki (the Wikipedia article title, if any), val_bn (valuation in USD billions as listed), year and month of that valuation,
url (the source the list cites), industry and country as listed. The list is not kept current: some companies have since listed, been bought,
shrunk or closed. Your job is to check each one and write a line ONLY for those that qualify today.

For each company:
1. Read its Wikipedia article (WebFetch https://en.wikipedia.org/wiki/<wiki title>) and, if needed, the cited url or the company's own site.
2. Leave it out if it is listed, was bought by a listed group, is closed, in insolvency, or has stopped trading. Leave it out if it is a current
   F1 partner (roster in brief_check.md) or you cannot establish what happened to it.
3. Capacity test: (c) applies only if the valuation or purchase of USD 1B or more is dated November 2023 or later (the list's own figure and cited
   url count as the page; use capacity_source = the cited url). Otherwise use (a): equity raised of USD 150M or more in total, stated on a page
   you fetched (rounds may be added up; say so). If neither can be shown, try (b) published revenue of USD 300M or more, then (d). If none can be
   shown, leave the company out and count it in your reply.
4. "group" = "Unicorn list". "theme" = the best fit from this list, or "" if none fits: Quantum computing | Nuclear & fusion energy |
   Prediction markets, betting & iGaming | Digital assets, stablecoins & crypto | Defence technology | Space & satellites |
   Robotics, humanoids & autonomous driving | AI infrastructure: data centres & GPU cloud | AI chips & semiconductors |
   AI models, agents & applications | Cybersecurity | EVs, charging & new mobility | Energy storage, renewables & grid |
   Consumer health, GLP-1, wearables & longevity | Sports, gaming, creator & entertainment | Neobanks, payments & trading apps |
   Consumer brands: beauty, fashion, food & drink | Travel, aviation & hospitality.
5. You do not need on_sheet.py for the input names (already checked). Do not add companies that are not in your input file.
