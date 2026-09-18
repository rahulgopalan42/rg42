# rg42

## F1 Sponsorship Prospector agent

`.claude/agents/f1-sponsorship-prospector.md` defines a Claude Code agent that
researches and ranks companies as Formula 1 sponsorship prospects with the
capacity to spend ~USD 3.5M per annum on sponsorship.

### Usage

From a Claude Code session in this repo, ask for example:

- "Use the f1-sponsorship-prospector agent to build a prospect list."
- "Use the f1-sponsorship-prospector agent to qualify Databricks as an F1 prospect."
- "Refresh the prospect report in `reports/`."

The agent qualifies affordability (revenue/funding gates), scores prospects on
budget capacity, strategic fit, and timing signals, and writes a ranked
markdown report with deep dives, suggested F1 properties to pitch, and target
buyer contacts. If the Clay MCP connector is available in the session, it uses
Clay to find companies and enrich decision-maker contacts.

Generated reports live in `reports/`.
