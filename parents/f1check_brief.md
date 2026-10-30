# Existing Formula 1 sponsorship check (knowledge only: no web, no Clay/Apollo/Lusha)

SPORTFIVE's F1 sales team needs to know which companies on its prospect list ALREADY have a Formula 1 deal, so those
rows can be highlighted. Today is 19 Oct 2026; use what you know up to mid-2026 (2025 and 2026 seasons).

## Input
`/home/user/rg42/parents/f1check_in/chunk_NNN.json`: rows `[key, name, domain, hq_country, sector, note]`.
`note` is what our research already says about an F1 link ("" if nothing).

## Task
For every row decide whether the company (the parent itself OR one of its brands / subsidiaries) currently holds any
of: an official F1 partnership (Formula 1 global / regional partner), an F1 team sponsorship or partnership (title,
principal, official partner, supplier with branding), ownership of an F1 team, or a Grand Prix title / official
partnership. Also count a deal that was publicly announced for 2026 or 2027.
- Report ONLY rows where you know of such a deal (current or recently ended). Do not list rows with no link.
- Status: "current" = active in the 2025 or 2026 season as far as you know; "former" = ended before 2025 (name the
  last year); "unsure" = you recall a link but cannot place the team or year.
- Never invent a deal. If you are not confident, use "unsure" or leave the row out.

## Output
`/home/user/rg42/parents/f1check_out/chunk_NNN.json`: a JSON array with one row per reported company:
`[key, status, deal, conf]` where `deal` <= 15 words names the counterparty and role (e.g. "Aston Martin F1 official
partner since 2024", "Mercedes-AMG F1 team partner", "owns Alpine F1 stake") and `conf` is "H" / "M" / "L".
Keys must be copied exactly from the input. Validate with
`/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/venv/bin/python -I`
(valid JSON, 4 fields, every key present in the input). Helper scripts go in the scratchpad folder named in your task.
Reply in 2 lines: rows checked, rows reported (current / former / unsure).
