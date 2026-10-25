# v7 OUTREACH TEMPLATE BRIEF (SPORTFIVE x Formula 1) - research agent instructions

## THE USER'S OWN APPROVED EXAMPLE (added 21 Oct) - match this phrasing style exactly

Hi Daphne,

Reaching out from SPORTFIVE - the authorized agency managing brands sponsorships for Formula 1 teams
working closely with McLaren, Haas, Audi & Mercedes to name a few.

A few of our Formula 1 teams are looking for an Official Autonomous Vehicle Partner, and Motional was
identified as a potential fit due to its driverless Ioniq 5 robotaxis now live on the Uber app in Las
Vegas.

- Your target audience: The customers you serve are the ride-hail and delivery platforms putting
  robotaxis in front of riders. Automotive and vehicle-technology brands of that profile are already
  in the sport: Toyota Gazoo Racing (Haas) and Snapdragon (Mercedes).
- Market Overlap: Motional's driverless Ioniq 5 robotaxis are available on the Uber app in Las Vegas,
  with Uber Eats and Lyft among its platform partners as it builds toward wider commercial service.
  The Formula 1 calendar aligns with the markets you are present in and expanding into: Las Vegas,
  where your vehicles already pick up riders, plus Miami and Austin.
- Shared Values: An F1 team puts its machines in public every race weekend, where one failure at
  speed happens in front of millions. Motional carries the same kind of exposure on city streets:
  driverless vehicles that have to earn trust ride after ride, in full public view.
- Market Reference: Zoox, your closest rival in purpose-built robotaxis, became a partner of Atlassian
  Williams this season as it opened service across Las Vegas, San Francisco, Austin and Miami. Two
  robotaxi brands are now competing for the same riders in Las Vegas, and one of them has its name
  alongside an F1 team all season.

Open to a short call to see if there is an alignment? If interested, we would love to host you at a
race to show you how partners are generating ROI.

Rahul / Major Motorsport Projects - Global Sales / SPORTFIVE

What this example fixes for your fields (these override anything below that conflicts):
- fit_reason is a CLAUSE that continues the sentence "...was identified as a potential fit": it must
  start with "due to" (lowercase), name one concrete, verified, recent fact about the brand, and end
  with a full stop. Example: "due to its driverless Ioniq 5 robotaxis now live on the Uber app in Las
  Vegas." Never start it with "The logic is simple".
- target_audience (B2B): two sentences in this shape: "The customers you serve are <who, plainly>.
  <Sector> brands of that profile are already in the sport: Brand (Team) and Brand (Team)." No spend
  figures and no audience statistics here.
- market_overlap: one sentence on where the brand operates or is expanding (specific, verified), then
  "The Formula 1 calendar aligns with the markets you are present in and expanding into: <real 2026
  races>" with one concrete tie where possible.
- shared_values: two sentences: what an F1 team does, then the brand's equivalent, plain words.
- market_reference: competitor or peer named with its relationship to the brand ("your closest rival
  in ..."), what it did in F1 and when, then one sentence on what that means for the brand.
- B2C brands: same four bullets plus "F1 Audience" with the fan stats from the stat bank.

You are writing the brand-specific parts of a Formula 1 team sponsorship outreach email for each
brand in your chunk file. The user (Rahul, SPORTFIVE, Major Motorsport Projects - Global Sales) sends
these to CMOs and CEOs. Accuracy is the product: one wrong roster fact or invented stat kills the
email and the sender's credibility. Every claim must be verifiable TODAY with a web source.

## What you return
Your final message must be ONLY a JSON array (no prose before or after), one object per brand in
your chunk, in this exact shape:

{
  "brand": "<exact name as given in the chunk file>",
  "legal_name": "<the company you identified, e.g. KoBold Metals Company>",
  "domain": "<official website domain, e.g. koboldmetals.com - verified by opening the site>",
  "hq": "<city, country>",
  "variant": "B2B" or "B2C",
  "designation": "<Official ... Partner>",
  "fit_reason": "<1 or 2 sentences>",
  "target_audience": "<2 to 3 sentences>",
  "market_overlap": "<2 to 3 sentences>",
  "shared_values": "<2 to 3 sentences>",
  "market_reference": "<2 to 3 sentences, or an empty string if proven absent>",
  "f1_audience": "<2 sentences for B2C brands; empty string for B2B brands>",
  "flags": ["<short flag>", "..."],
  "sources": ["<url>", "..."]
}

The fixed parts of the email (opener, hook sentence, closing invitation, signature) already exist in
the user's Word master. Your text is merged into it like this:

  Hi [First name],
  [opener - fixed]
  A few of our Formula 1 teams are looking for an [designation], and [brand] was identified as a
  potential fit. [fit_reason]
  Your target audience: [target_audience]
  Market Overlap: [market_overlap]
  Shared Values: [shared_values]
  Market Reference: [market_reference]        <- bullet removed entirely when empty
  F1 Audience: [f1_audience]                  <- B2C brands only
  [closing: open to a short call to explore further; happy to host at a race to show how partners
   generate ROI - fixed]
  Rahul / Major Motorsport Projects - Global Sales / SPORTFIVE

So: never repeat the opener, the hook, the closing or the signature in your fields. Never start a
field with its label. Write complete sentences. Total of your fields: roughly 130 to 190 words.

## Step 1 - identify the brand
Names are dictated and can be misread. Identify the most likely company given that this whole batch
is critical minerals, battery materials, mining technology and mineral exploration. If a name could
be more than one company, build the most likely one and put the alternative in flags
("Identity: built as X; could also be Y - confirm").

## Step 2 - research the brand (web, every brand)
Establish with sources: what it does and sells; who it sells to (named customers and investors where
verifiable); markets where it operates or is expanding (countries, plants, projects); scale (revenue,
funding, valuation, listing); HQ; direct competitors; recent news that signals marketing intent.
Only verified specifics go in the email.

## Step 3 - verify the grid (web, every brand) before writing market_reference
- Fetch https://f1salaries.com/sponsors/ (the user's preferred source for the current partner
  landscape) AND https://sector.world/f1-the-grid/ fresh as the roster baseline, then run targeted searches:
  "<category> partner F1 2026", "<nearest team> <category> partner", and each direct competitor by
  name plus "Formula 1". New deals are announced weekly; never rely on memory.
- The 2026 grid has ELEVEN teams: McLaren (Mastercard title), Mercedes-AMG Petronas, Oracle Red Bull
  Racing, Scuderia Ferrari HP, Atlassian Williams, Visa Cash App Racing Bulls, Aston Martin Aramco,
  TGR Haas (Toyota Gazoo Racing title), Audi Revolut, BWT Alpine, Cadillac.
- Leads worth checking for this batch (verify before citing): Komatsu is a Williams principal partner
  (mining equipment). Toyota titles Haas. Ford supplies Red Bull power units from 2026. General
  Motors owns the Cadillac team. Honda powers Aston Martin from 2026. Audi runs its own team.
  Mercedes runs its own team. Aramco titles Aston Martin and runs F1's sustainable fuel work. Petronas
  titles Mercedes. Shell is at Ferrari. Mobil 1 is at Red Bull. If a brand's own customer, investor or
  parent is on the grid, say so plainly: that is the strongest proof there is.
- Formula E, Extreme E, IndyCar, WEC and NASCAR partners are NOT Formula 1 partners. Never cite them
  as F1 references.
- Team attributions in brackets with roster spelling, e.g. Komatsu (Williams), Aramco (Aston Martin),
  Toyota (Haas). Series-level partners are attributed as (Formula 1).

## Field rules (v7, user-approved)

designation: "Official <Category> Partner". Make it specific to what the brand sells, and different
from every other brand in the batch list below (no two brands get the same category).

fit_reason: the commercial logic in plain words, completing the hook. Pattern: "The logic is simple:
the <sectors / companies> you sell to are already partners in this sport, and race weekends are where
their senior decision makers show up in person." Adapt to the brand; if their customer or investor is
literally on the grid, lead with that.

target_audience (B2B): who they sell to, mapped to the grid. Pattern: "Your customers, <named ICP
sectors>, are already invested in this sport. Those sectors are spending more than $X on F1
sponsorships in 2026. Some of the names from those sectors: Brand (Team), Brand (Team)." Then one
plain sentence that Formula 1 is now a major B2B platform: 350+ business partners, the highest
concentration of business decision makers in sport, and 66% of Paddock Club guests are senior
executives. Spend figures come ONLY from the stat bank below; sum only the sectors that map cleanly
and round DOWN ("more than"). Never invent a figure for a sector the bank does not list (there is no
"mining" line: use energy/utilities, automotive or industrial only where the brand's customers truly
sit there, otherwise leave the spend sentence out).
target_audience (B2C): the consumer they sell to and why F1's fan base is that consumer, in plain
words, no stats here (stats go in f1_audience).

market_overlap: where the brand operates or is expanding, matched to real 2026 races and F1 markets.
Say plainly that Formula 1 is present in the markets they are present in, growing in or expanding
into. Only cite races that exist on the 2026 calendar (verify any race you name; three US races are
Miami, Austin and Las Vegas; Madrid joins in 2026; Zandvoort's last Dutch GP is 2026). Home-race
lines are good when real (an Australian brand and the Australian GP, a Canadian brand and Montreal).

shared_values: the operational fit, two or three short sentences: what F1 teams do, what the brand
does, and how the brand could add value inside a team or the sport. Sustainability alignment belongs
here ONLY when real and specific: F1 runs 100% sustainable fuel from 2026, targets net zero by 2030,
and the 2026 power units roughly triple the electrical power, which makes batteries and their supply
chain a live topic in the sport. No metaphors, no clever lines, nothing a copywriter would reach for.

market_reference: a brand the reader would see as a competitor or a relevant peer, and what it does
in Formula 1, specific and unique to this brand. Work down the ladder and use the highest honest
rung: (1) a direct competitor on the grid; (2) a genuinely similar company, the same buyer's world,
on the grid or at series level, then note the brand's own seat is open; (3) nothing honest exists ->
empty string, and a flag "Market reference dropped: searched <what you searched>". A false
neighbour costs more than a dropped bullet. Never say how many teams have a category open.

f1_audience (B2C only): go straight into the stats, no "according to a survey" framing: 827M fans in
2025 (+12% in a year), 42% female, 43% under 35, 1.83bn total audience in 2025, 6.7M race attendance.
Add a purchase-consideration lift only where the market fits (US fans 32% more likely to consider a
sponsor's product; Gen Z 39%; women 41%).

## Stat bank (the ONLY numbers allowed in any field)
- 350+ business partners across the grid; each team carries 25+ partners.
- Highest concentration of business decision makers in sport: fans index 160 for general management
  and corporate strategy roles (general population = 100).
- 66% of Paddock Club guests are senior executives (use exactly this wording).
- 2026 sector spend on F1 sponsorship, team + series ($M): technology, media and telecom ~706;
  financial services ~529; energy and utilities ~269; clothing and accessories ~301; consumer goods
  ~191; beverages ~255; automotive ~232; industrial ~69; travel and tourism ~148; construction and
  real estate ~32; logistics ~62.
- Fans: 827M (2025), 42% female, 43% under 35. 2025 total audience 1.83bn; average Grand Prix
  audience 76.1M; on-site attendance 6.7M. Purchase consideration: US +32%, Gen Z +39%, women +41%.
- US: three races (Miami, Austin, Las Vegas); two American teams from 2026 (Haas and Cadillac).
Any other number is prohibited. Revenue or funding figures about the brand itself may appear only
in flags, never in the email fields.

## Tone and QC scrub (every field)
- Simple English a busy CEO reads in one pass. Short, direct sentences. Sounds like a sharp human
  wrote it for this one brand. No jargon, no filler words, no hype.
- Forbidden characters and words: em dashes and en dashes (use commas or full stops), exclamation
  marks, "actually", "genuinely", "honestly", bold or markdown, bullet symbols, quotation marks
  around phrases. Dollar figures appear only in the target_audience spend sentence.
- No claims about how many teams have a seat open. No "cutting edge", "revolutionary", "synergy".
- Never cross-contaminate: read the brand name, then each field, and confirm they match.

## Compliance and flags (flags are for the user, never in the email)
- Capacity read: can the brand comfortably spend USD 3.5M+ per year now, or on clear trajectory?
  Grade it: "Capacity: strong" / "Capacity: soft note" / "Capacity: firm caution" / "Capacity: hard
  caution", with one supporting fact (funding, revenue, listing).
- China, India or Brazil HQ: build it, add flag "HQ override: China/India/Brazil HQ".
- Defense-led or state-owned customer bases: flag it; mission-level language only in the email.
- Same house: if two brands in the batch share a parent, flag it.
- Batch collisions: the batch list below contains direct competitors (several lithium extraction
  companies, several AI mineral explorers, several recyclers). Give each a different designation and
  a different reference brand or angle, and flag "Collision: competes with X in this batch - sequence
  sends".
- Governance: recent settlements, distressed balance sheets, activist situations -> flag only.
- Sanctions or Entity List company: do not build; return the row with empty fields and a flag
  "DECLINED: <reason>".

## The full batch (for designation and reference differentiation)
Kobold Metals, Standard Lithium, Lilac, EnergyX, Redwood Materials, US Strategic Metals,
Alta Resource Technologies, EACON, Principal Mineral, Nth Cycle, EARTH AI, Element3,
pH7 Technologies, Scout Discoveries Corp.

## EXEMPLARS (approved structure, 25 Oct 2026, revision 2) - supersede all earlier field rules
B2B hook: "A few of our Formula 1 teams are looking for an <Designation>, and I wanted to share why this could
make sense for <Brand>." No "identified as a potential fit due to" sentence; its reason moves into a bullet.
B2C hook keeps "...and <Brand> was identified as a potential fit due to <reason linking the brand to F1>."
Target audience (both): starts "Your target customers are ..." and names PARTNERS as well as customers; then 3-4
relevant grid names of that kind. B2C adds "Formula 1 Audience" with brand-relevant depth from the stat bank
(premium buyers 132, research online 126, tech interest 146, brand loyalists 200, women 74% of new fans, etc.),
not just headline fan counts. Drop Market Reference when no honest peer exists. Plain, commercial, no drama.
ROSTER FIX 25 Oct: WHOOP is at FERRARI (Team Partner, Official Health and Fitness Wearable Partner, 2026), not
Red Bull as verification.md says. Eight Sleep = Aston Martin (Feb 2026, one year).

B2B - SentinelOne
- Hook: ...Official Endpoint Security Partner, and I wanted to share why this could make sense for SentinelOne.
- Your target audience: Your target customers are large enterprises, governments and the managed security
  providers that protect them. You also build with partners like AWS and Google Cloud, and Lenovo ships your
  security on its PCs. Those partners are already in Formula 1: AWS (Formula 1), Google (McLaren) and Lenovo (Formula 1).
- Market Overlap: SentinelOne is headquartered in California, was founded in Israel and protects customers
  worldwide. The Formula 1 calendar aligns with the markets you are present in and expanding into: Miami, Austin
  and Las Vegas at home, plus 21 more races across Europe, the Middle East and Asia.
- Shared Values: An F1 team runs on data, from the factory to the garage at every race, and that data is a
  constant target. SentinelOne protects the same kind of operation, using AI to find and stop attacks on laptops,
  servers and cloud systems.
- Market Reference: Bitdefender, a direct competitor in endpoint security, has been Ferrari's exclusive
  cybersecurity partner since 2022 and extended the deal in October 2025. This season its name moved further onto
  the car, and Ferrari's security analysts use its technology to check and prioritise alerts.
- Flag: Bitdefender holds cybersecurity exclusively at Ferrari; confirm which other teams have the category open.

B2C - Oura
- Hook: ...Official Smart Ring Partner, and Oura was identified as a potential fit due to its growth among women,
  who make up 74% of new Formula 1 fans, and its expansion outside the US.
- Your target audience: Your target customers are health-conscious adults who want to understand their sleep,
  recovery and fitness, and you reach them through retail partners in more than 4,600 stores worldwide. Health and
  fitness brands are already in the sport to reach the same people: Eight Sleep (Aston Martin), Technogym
  (Ferrari) and Optimum Nutrition (McLaren).
- Market Overlap: Oura is a Finnish company, with international markets driving much of its growth. The Formula 1
  calendar aligns with the markets you are present in and expanding into: Silverstone and Barcelona in Europe,
  Suzuka in Japan, and Miami, Austin and Las Vegas in the US.
- Shared Values: An F1 team tracks its drivers' sleep, recovery and readiness as closely as the car's data,
  because both decide the result. Oura gives its members the same kind of insight every morning.
- Market Reference: WHOOP, your closest rival in health wearables, joined Ferrari this season as Official Health
  and Fitness Wearable Partner. Ferrari's medical staff use it with the drivers to track sleep, stress and
  recovery. Your nearest competitor is now part of how an F1 team prepares its drivers.
- Formula 1 Audience: Formula 1 had 827 million fans in 2025, and 74% of new fans are women. F1 fans are the most
  likely of any major sport's fans to buy premium versions of products (index 132) and to research online before
  buying (126), and they index 146 for interest in technology (general population = 100). US fans are 32% more
  likely to consider a sponsor's product, rising to 41% among women.
- Flags: Technogym (Ferrari) and Optimum Nutrition (McLaren) are multi-year deals with no 2026-dated
  confirmation found; re-check at send. Oura filed for a Nasdaq IPO in Sept 2026 (quiet-period sensitivity).

## REVISION 3 (25 Oct): value-led Market Reference + B2B pipeline bullet
- Market Reference must say what the peer GETS from the deal (customer reference, hospitality for its buyers,
  research credential, product use by the team), from verified sources; not just that a deal exists.
- B2B adds a fifth bullet "Enterprise Pipeline & B2B Activations": team partner networks (25+ partners per team,
  name 3-4 grid partners that are the brand's type of buyer), compliant introductions, race-weekend hosting of the
  brand's own prospects, and the locked line "66% of Paddock Club guests are senior executives". B2C keeps
  "Formula 1 Audience" instead. Merge column: Pipeline (B2B only).

SentinelOne Market Reference: Bitdefender, a direct competitor in endpoint security, has been Ferrari's exclusive
cybersecurity partner since 2022, and it gets more than a logo on the car. Ferrari uses its technology to hunt
threats, which makes Ferrari a working reference customer, and the deal includes driver meet-and-greets, factory
tours and garage access that Bitdefender can offer its own buyers. Ferrari extended it in October 2025.
SentinelOne Pipeline: Each F1 team works with 25 or more partners, and many are large enterprises with the
security needs you solve, such as Mastercard (McLaren), Barclays (Williams), Aramco (Aston Martin) and Shell
(Ferrari). Teams make compliant introductions across that network, and 66% of Paddock Club guests are senior
executives. You can also host your own CISO prospects at races, with time in the garage and with the team's
technology staff.
Oura Market Reference: WHOOP, your closest rival in health wearables, joined Ferrari this season. Its logo is on
the cars and drivers, its devices are available to team members, and it is writing a joint research paper with
Ferrari's medical staff on sleep, stress and recovery. That gives WHOOP a scientific credential with one of the
best-known teams in sport, which it can share with its own members.

## REVISION 4 (25 Oct): pipeline bullet REMOVED; blended into B2B target audience (supersedes revision 3)
B2B target audience = customers + partners on the grid, 3-4 enterprise names of the buyer type, one line that
teams introduce partners to one another, and B2B audience data (highest concentration of business decision
makers in sport; 66% of Paddock Club guests are senior executives). Four bullets for B2B, five for B2C.
SentinelOne target audience: Your target customers are large enterprises, governments and managed security
providers, and you build with partners like AWS, Google Cloud and Lenovo. Those partners are already in Formula 1:
AWS (Formula 1), Google (McLaren) and Lenovo (Formula 1), alongside enterprises you sell to, such as Mastercard
(McLaren), Barclays (Williams) and Aramco (Aston Martin). Formula 1 has the highest concentration of business
decision makers in sport, 66% of Paddock Club guests are senior executives, and teams introduce their partners to
one another, so a race weekend puts you in the room with the buyers you want.
