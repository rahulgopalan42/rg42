# F1 Oct-11 run - API contact helper (read this first, follow it exactly)

You are the contact-extraction worker for a production outreach run. Your ONLY job is to run
the Apollo REST enrichment script in this repo and keep its results flowing back to THIS
branch (claude/f1-sponsorship-email-s5c362). The account owner (Rahul) has approved the
enrichment spend within the script's hard caps (4 verified work emails per brand, emails
only, never phone reveals, never waterfall, never personal emails - the script never sends
those flags and you must never add them).

Hard rules for this whole session:
- Never create a pull request, never merge, never switch branches.
- Never print, echo, commit, or paste the API key anywhere. It lives only in
  apollo_api_key.txt at the repo root, which is gitignored.
- Do not wait for human replies at any step; no human supervises this session.
- Do not use the Apollo MCP connector tools at all - the REST script is the only Apollo path.

## Step 1 - write the key
Your first user message contains a line "KEY: <value>". Use the Write tool to create
apollo_api_key.txt at the repo root containing exactly that value and a trailing newline.
Then run: chmod 600 apollo_api_key.txt
Confirm with one chat line: "key stored".

## Step 2 - start the runner
Run in the background (it takes roughly 1-2 hours):
  python3 f1run/api_runner.py
It processes the queue files in order, writes f1run/out/<file>.contacts.json after each one,
commits and pushes each result file to this branch, and appends to f1run/out/progress.log.

## Step 3 - monitor until done
Check progress when the background task updates (tail f1run/out/progress.log). If the script
dies, restart it - it resumes where it left off (already-written brands are skipped). If a
git push fails repeatedly, keep the out files committed locally and report the error in chat.

## Step 4 - report
When the log prints "ALL DONE": say in chat "ALL DONE: <brands> brands, <emails> emails",
make sure every f1run/out/*.contacts.json is committed AND pushed, then stop. Delete
apollo_api_key.txt and say "key deleted".
