# LiveKit x SPORTFIVE: F1 Intro Call Script

**The call:** intro call with [Michelle Schroeder, VP Marketing] at LiveKit (from the outreach email, confirm), following Rahul's outreach about Formula 1. Joining from SPORTFIVE: Rahul, Bjorn and George. The email pitched LiveKit as a possible Official Real-Time Communications Partner, built on its place at the center of voice AI (ChatGPT's voice mode) and the live voice links an F1 team runs on, with Cisco Webex at McLaren as the reference.

**How to use this:** Spoken lines are in quotes; notes to you are in [brackets]. Say it your own way, and glance at it, don't read it.

---

## Boilerplate: what LiveKit does

- **About LiveKit:** LiveKit is a San Francisco company, founded in 2021 by Russ d'Sa and David Zhao, that builds the open-source software and cloud network apps use to hold live voice and video conversations, more and more of them between people and AI agents. Developers build on its free open-source framework, and companies pay to run what they build on LiveKit Cloud, with phone lines, AI model access, testing and monitoring built in. ChatGPT's voice mode runs on it, and LiveKit names Salesforce, Tesla, SAP, Meta, Microsoft and Spotify among its customers, says "more than 10% of the Fortune 500" build on it, and says about a quarter of US 911 dispatch centers use it. It raised a $100 million Series C at a $1 billion valuation in January 2026, led by Index Ventures with Salesforce Ventures, taking the total raised to about $183 million. Since May it has hired a Chief Revenue Officer and new sales, marketing and finance leaders to grow its enterprise business, and it says it is working to become "the default platform" for AI agents across voice, video and what it calls physical AI, meaning robots and devices.
- **In one line, if someone asks on the call:** "They build the plumbing that lets apps and AI agents talk and listen in real time. If you've used ChatGPT's voice mode, that conversation ran on their tech."

## Who they sell to: target sectors, ICP and goals

*[Checked 30 October 2026 against LiveKit's site, customer stories, docs, pricing and careers pages, its releases, and reporting. "Verified" means an independent source; "their claim" means LiveKit says so; "estimate" means a third party's figure; "our read" is inference.]*

**The short version: two audiences.** Developers pick LiveKit: open source, a free tier, docs, community, and self-serve plans from $50 and $500 a month (pricing page). Enterprises sign: custom contracts with SSO, support SLAs, region pinning and a signed HIPAA agreement, sold by a sales team that got a new CRO in May 2026. The developer gets LiveKit in the door; a CTO or whoever runs customer service signs the big deal (our read, from their pricing, hiring and customer stories).

**1. Target sectors (most evidence first)**

- **AI labs and AI-native voice products:** ChatGPT's voice mode runs on LiveKit (verified, TechCrunch, January 2026). They also name Meta, Microsoft and SpaceXAI, formerly xAI (their claim, September 2026 release), and voice-agent companies such as Retell, Decagon, Cresta and Ultravox sit on their customer page (their claim).
- **Contact centers and customer service:** Salesforce's Agentforce voice agents, and Tesla's sales, support, insurance and roadside lines (Series C post, their claim). "Call center" is a named use case in their docs; they sell phone numbers and SIP, launched Twilio and WhatsApp connectors on 1 September 2026, and are hiring a Staff Product Manager for Telephony. Their investor Index says voice agents are "becoming the first line of interaction in call centers".
- **Healthcare and telehealth:** stories from Assort Health (patient communication) and Acuity Health (patient access, 21 October 2026), Hello Patient (hospital workflows, 2025), plus Zocdoc and Headspace logos (their claim). Telehealth is a named docs use case, and they sign HIPAA BAAs.
- **911 and public safety:** about a quarter of US 911 dispatch centers use LiveKit (their claim, April 2025); TechCrunch listed "911 emergency service operators" among customers (January 2026). Axon, which agreed to buy the 911 platform Prepared in September 2025, is on their customer page (their claim; nothing says Prepared runs on LiveKit).
- **Robotics and physical AI:** the tagline is "voice, video, and physical AI agents"; stories from Skydio (drone teleoperation) and Polymath Robotics (remote heavy machinery); a robotics post in August 2026; Nvidia on the logo wall (their claim).
- **Enterprise software:** SAP (customer story quoting its Chief AI Officer), Salesforce and Oracle (their claim).
- **Consumer, media and learning:** Spotify, Coursera, Tinder, Whatnot, Fanatics, and Playback, an app for watching sports together (their claim).

**2. Ideal customer profile**

- **Size and stage:** two shapes. AI-native startups and scale-ups building a voice product (self-serve first), and large companies with heavy call volumes or customer-facing AI ("more than 10% of the Fortune 500", their claim, May 2026). Inferred from the customer list and pricing tiers.
- **Geography:** mostly the US today (HQ San Francisco; about 76% of staff in North America, Revelio estimate, March 2026). Europe looks next: an Account Executive and a Solutions Architect in Germany, a Solutions Architect in the UK, engineers in the UK and Ireland (careers page, 30 October 2026); SAP and Deutsche Telekom are on the logo wall. A Spanish and English engineer role in Miami and LA hints at Spanish-language voice (our read).
- **Maturity:** has engineers who write code (agents are built in Python or Node), wants voice or video in production, and needs uptime, low lag and compliance (they claim SOC 2 Type 2, HIPAA and GDPR).
- **Trigger events (our read, from stories and leadership quotes):** moving a voice agent from pilot to production ("Enterprises are moving beyond AI pilots", their CRO, May 2026); a homegrown stack that stops scaling (Retell's CTO: "We recently moved from a homegrown WebSocket stack to LiveKit Cloud"); contact-center cost and staffing pressure; a voice feature launch in a consumer app; a compliance need (BAA, region pinning, zero data retention); spikes in concurrent calls.

**3. Who signs and who uses it**

- **Users and champions:** developers and engineers (300,000+, their claim); at startups, the CTO (the Retell, Polymath, Serve and Acuity stories all quote CTOs).
- **Economic buyers at enterprises (our read):** CTO or CIO, Chief AI Officer (SAP's is quoted), VP Engineering or Platform, and the head of customer experience or contact-center operations where the agent handles calls.
- **How they buy:** bottom-up first; Index said growth was "almost entirely bottom-up, with barely any GTM machinery behind it" (January 2026). Then sales-led enterprise deals: usage-based, credit-based pricing (job ad), forward deployed engineers, and since May a CRO (Tom Davies, ex-Grafana Labs and Snowflake) and a Regional VP of Sales. Deal size and sales cycle: not disclosed.

**4. What their customers want**

- **The job:** put a voice or video agent in front of customers, patients or callers that works live, every time, on the phone or in an app, with any AI model they choose.
- **Pains removed, in customers' words:** scale ("Not having to worry about our ability to scale has been massive", Playback's CTO); lag ("Low-latency video streaming is existential for any robotics company", Polymath's CTO); testing ("We ran about a hundred real production calls through it and got to a 98% pass rate before we cut anyone over", Serve's CTO); lock-in ("use any model provider", Assort Health).
- **What LiveKit promises (their claim):** 99.99% uptime, under 100ms latency worldwide, and a faster road to production ("Reliability and accelerating time to production often seem at odds, but with LiveKit's Agent Platform, we achieved both!", Podium).

**5. Named reference customers (most recognisable first)**

- **Verified:** OpenAI, ChatGPT voice mode (TechCrunch). Salesforce Ventures invested in the Series C (Salesforce as a customer is their claim).
- **Their claim:** Salesforce (Agentforce voice agents); Tesla (sales, support, insurance, roadside help); SAP (voice in its enterprise AI); Meta, Microsoft and SpaceXAI (September 2026 release); Spotify (also reported by SiliconANGLE); Skydio (drone teleoperation); Coursera; Assort Health and Acuity Health (patient calls); about a quarter of US 911 dispatch centers (2025).

**6. What LiveKit is trying to achieve (next 12 to 24 months)**

- **Be the default:** "as we work to become the default platform" (Russ d'Sa, September 2026); "2026 will be the year voice AI will be broadly deployed" (January 2026).
- **Move upmarket:** a CRO, a Regional VP of Sales, a VP Finance and Michelle as VP Marketing, announced 21 May 2026 "to accelerate enterprise growth"; an earlier revenue-marketing role was to build enterprise account-based marketing from scratch.
- **Go international:** sales and solutions roles in Germany and the UK; engineers in Europe and Asia-Pacific (careers page).
- **Widen the product:** from voice into video and robots. Agent Builder, Inference, Phone Numbers and Observability (January), Agent Simulations (October), and Loophole Labs (bought September 2026) to start agents in under three seconds and get closer to "essentially unlimited concurrent agents" (their plan).
- **Build the brand:** senior brand designer roles open; community events like DevDay in San Francisco. No IPO talk found.

**7. What this means for F1**

- **Their sectors are in the paddock:** enterprise software and cloud (Oracle at Red Bull, Salesforce with F1, Microsoft with Mercedes as reported, Google Cloud at McLaren, AWS with the sport); companies with big customer-service operations (Barclays at Williams, Etihad at McLaren, Qatar Airways with F1); communications (Cisco at McLaren); and voice AI already (ElevenLabs at Audi). Healthcare, 911 and robotics are thin in the paddock (our read), so they're stories, not guest lists.
- **The room:** 66% of Paddock Club guests are senior executives, CIOs and CTOs included, and F1 fans index at 160 for business decision makers, the highest in sport.
- **A guest list built on their ICP:** CTOs and Chief AI Officers at enterprise software firms; heads of customer experience and contact-center operations at banks, airlines, insurers, telcos and car makers; digital leads at health systems; CTOs of the AI-native voice companies they work with. No 911 or other public-sector guests without a compliance check.
- **Markets:** the three US races first (Miami, Austin, Las Vegas, plus F1's Business Summit in Vegas). Then Europe, matching the UK and Germany hiring, with Silverstone the obvious one. More than twenty race weekends to choose from.

**8. Two lines Rahul can use**

> "From what I can see, it starts with developers picking you, and then it's a CTO, or whoever runs customer service at a big company, who signs. And what they want is a voice agent that works live, every time, at scale. Is that fair?"
>
> "And it seems to matter most in contact centers, healthcare, 911, and now robots. Which of those is growing fastest for you?"

## 1. Brand snapshot (not spoken)

*[Re-checked 30 October 2026 (first written 25 October). "Verified" means independent reporting; "their claim" means LiveKit's own site or releases; "estimate" means a third-party figure.]*

- **What they do (verified):** open-source software and a managed cloud for live voice and video, now pitched as the platform to "build voice, video, and physical AI agents" (their tagline). The pieces: the open-source media server, the Agents framework, LiveKit Cloud, phone numbers and telephony, inference across model providers, agent testing (Simulations) and observability.
- **Who and where (verified):** founded 2021 by Russ d'Sa (CEO) and David Zhao, as an open-source project in the video-call boom. HQ San Francisco, remote-first. Headcount: about 109 in March 2026 (Revelio, estimate), about 136 per a June 2026 job listing (estimate), plus eight from Loophole Labs. Say "around 110 to 140".
- **Model (verified):** the open source is free; the money comes from LiveKit Cloud (usage-based: Build free, Ship from $50 a month, Scale from $500, Enterprise custom) and enterprise contracts. Revenue not disclosed; third-party estimates disagree too much to use.
- **Funding (verified):** $100M Series C at a $1B valuation, 22 January 2026, led by Index Ventures with Salesforce Ventures, Hanabi Capital, Altimeter and Redpoint; $183M raised in total. Before that, a $45M Series B in April 2025.
- **Customers:** ChatGPT's voice mode (verified). Their claim: Salesforce, Tesla, SAP, Meta, Microsoft, SpaceXAI (xAI's new name), Spotify, Oracle, Nvidia, Skydio, Coursera, and about a quarter of US 911 dispatch centers. Detail in "Who they sell to".
- **Scale (their claim):** 300,000+ developers (100,000+ in April 2025; 200,000+ per Index in January 2026), 3bn+ calls a year, 99.99% uptime, under 100ms latency, the Agents framework downloaded over 1M times a month, "more than 10% of the Fortune 500".
- **Last 90 days (verified unless marked):** bought Loophole Labs on 24 September (eight engineers; agent starts under three seconds, in production "over the next several weeks", their plan). Twilio and WhatsApp calling connectors (1 September). Agent Simulations for testing voice agents (8 October). Per-second billing, PII redaction and an "expressive mode" for more human-sounding agents (August). Acuity Health story (21 October). Sales hiring in Germany and the UK. No new funding, layoffs or exec departures found.
- **Leadership (verified, LiveKit release, 21 May 2026):** Tom Davies, CRO (ex-Grafana Labs, Snowflake); Megan Barros, Regional VP of Sales; Cameron Huang, VP Finance; Michelle Schroeder, VP Marketing (previously CMO of PolyAI, which builds voice agents for customer service; 13+ years in B2B tech marketing).
- **Sport and marketing:** no sports sponsorship found (fresh search, 30 October 2026). Marketing is developer-led: open source, docs, DevDay and meetups in San Francisco, developer advocates. The May hires look like the start of an enterprise and brand function (our read).

**In plain English:** "Developers use their free tools to build apps and agents that talk; companies pay LiveKit to run them live, reliably, at scale."

## 2. The opening

### A. Hello and who we are (30 seconds)

*[Check the invite's time zone: San Francisco is eight hours behind Hamburg until the US clocks go back on 1 November, then nine. Michelle's location isn't confirmed.]*

> "Hi Michelle, thanks for making the time, I appreciate it. I know you get a lot of emails, so thanks for picking this one up.
>
> I'm Rahul, I look after brand partnerships in SPORTFIVE's Formula 1 business. And I've got Bjorn and George with me."

*[Bjorn and George: a quick hello, one line each, no pitching. Then:]*

> "Just so you know how we work. We don't sell for one team. We work across all eleven, and we start from what the brand wants, then look at what fits. The rights holders pay our fee, so none of this costs you anything. And today's a conversation, not a pitch."

*[If they ask why not go straight to a team: "You could. We worked exclusively with Mercedes and Ferrari for more than twelve years, and we gave that up on purpose so we could work brand-first across all eleven teams. So the advice isn't tied to one car."]*

### B. Why I reached out (20 to 30 seconds)

> "What I enjoy most about this job is talking to very different brands, and I think LiveKit's one of the more interesting ones. What you're doing is quite interesting, especially how much of voice AI now runs on you, how your buyers have gone from developers to big companies, and the fact it all has to work live, with no second take. That's pretty much how an F1 team runs too, live voice between the driver, the pit wall and the factory. So a conversation about Formula 1 felt like it made a lot of sense."

*[Only if they ask for more. X, the layer voice AI runs on: ChatGPT's voice mode runs on LiveKit (TechCrunch, January 2026), and the Agents framework is downloaded over a million times a month (their claim). Y, the buyer moving up: Salesforce's Agentforce and Tesla in the Series C post, Salesforce Ventures in the round, a CRO from Snowflake and Grafana hired in May, and "more than 10% of the Fortune 500" (their claim). Z, it has to work live: 99.99% uptime, under 100ms latency, and about a quarter of US 911 dispatch centers (their claims). The F1 angle in one sentence: a team is a live voice operation under pressure, and the paddock is a room of the senior buyers LiveKit now needs to win.]*

### C. Handing over to them

> "But that's all from the outside, so I'd love to hear it from you. Where's LiveKit right now, what are you focused on for the next year, and what made you take the call?"

*[Then listen and take notes. Pick from section 4 as it flows; don't run the list in order. If they ask "why would a team want us?", go to section 3. If they ask "so where do you see us fitting?": "I don't know yet, and I'd be guessing. If you pushed me, I'd look at hosting the right enterprise buyers at a US race and a real working story around voice, and only something bigger if it earns it. But tell me more first."]*

## 3. If they ask: "Why is this category open? Why would teams want this?"

*[The answer Rahul expects to need most. Keep the last two lines in.]*

> "Good question, and I'll give you the real answer, not the sales one. Tech's got quite saturated in F1. It's now the biggest sponsorship category for the teams, and Reuters reported eight new AI deals in six months earlier this year. Oracle's on the Red Bull, HP's on the Ferrari, Atlassian's on the Williams, Google Cloud's with McLaren, and Microsoft's been reported with Mercedes. Even AI voice has a name in it now, ElevenLabs with Audi, mostly for content and fans.
>
> So what teams notice now is a partner with one clear, hard job, and a story the paddock hasn't heard a hundred times.
>
> And live is that story for you. A race weekend is a live operation, with the track and the factory talking all weekend, on more than twenty race weekends across five continents. There's no second take, which is exactly the problem you solve. And the people you're now selling to, CTOs and whoever runs customer service at banks, airlines and car makers, are the kind of people teams host every race weekend.
>
> Whether that seat's free at a given team is what we check properly. I won't tell you it's open everywhere."

**Short version, if there's no time:**

> "Tech's quite saturated in F1. It's the biggest category for the teams, and even AI voice has a name in it, ElevenLabs with Audi. So what stands out is one hard job and a fresh story, and live is yours, because a race weekend has no second take and the paddock's full of the buyers you're after. Whether the seat's free at a given team is what we'd check properly."

*[On the outreach email: it said "A few of our Formula 1 teams are looking for an Official Real-Time Communications Partner". If Michelle quotes it back, stay consistent without going further: "What I meant is there are teams we work with where a real-time comms partner like you could make sense. Which ones, and whether the seat's free, is exactly what the grid mapping tells us." Never say a named team is looking, and never say the category is open. The email also named McLaren, Haas, Audi and Mercedes as teams we work with closely; McLaren has Cisco Webex and Audi has ElevenLabs, so don't lead with either.]*

*[If they say "ElevenLabs is at Audi, so isn't voice taken?": "At one team, and as it was announced it's mostly content and fans. Exclusivity's different at every team, which is what the mapping checks. It probably means Audi isn't where we'd start."]*

*[If they push, "so which teams?": "That's the grid mapping, and it's the first thing we do after this call. I'd rather come back with names I can stand behind than guess today."]*

*[Backing, if they want proof: Reuters reported on 4 May 2026 that technology is now the top spending category for F1 teams (SponsorUnited; the dollar figure is background only) and that Ampere Analysis counted eight new AI partnerships in the previous six months, including CoreWeave with Aston Martin. CrowdStrike has been Mercedes' cybersecurity partner since 2019. Audi named ElevenLabs an official partner on 29 January 2026, for fan engagement and content, "exploring" use at the track. Sources in prep notes.]*

## 4. Questions to ask them

**1. Priorities**

> "You raised in January, you brought in a new sales and marketing team in May, and you've shipped a lot since. What's the one thing that has to go right for LiveKit in the next year?"

*[Follow-up: "Is that more about developers, or about landing the big enterprise accounts?" If they say enterprise: the room and the credibility story matter most; lean on sections 5 and 6.]*

**2. Who signs now**

> "When a big company picks LiveKit today, who's in the room by the end? Is it still the engineer, or a CTO, or the person who runs customer experience?"

*[Follow-up: "Has that changed since Tom and the new sales team came in?" If they say "it starts with a developer and ends with a CTO": that's the two-audience story. Developers get content and a real build; executives get hospitality.]*

**3. Which sector's growing fastest**

> "From the outside I'd guess contact centers, healthcare, 911 and robotics. Which of those is growing fastest, and is there one you want to win that you haven't yet?"

*[Follow-up, the room question: "If I gave you a paddock weekend tomorrow, which five accounts would you bring?" If they name banks, airlines, insurers or car makers: those categories are already in the paddock (section 7). If healthcare or 911: those buyers are thinner there, and 911 buyers are public bodies, so think story and content more than hospitality.]*

**4. Markets**

> "Where's the growth coming from? Is it still mostly the US, or is Europe starting to matter? I noticed you're hiring sales people in Germany and the UK."

*[Follow-up: "Anywhere else you're about to put people on the ground?" Note the US races (Miami, Austin, Las Vegas) and Silverstone against their answer.]*

**5. Marketing today**

> "You joined in May, so I'm curious how you see it. From the outside the marketing looks very developer-led. Open source, docs, community. Is that fair? And what's the bit you want to build next?"

*[Follow-up: "Do you want people outside the developer world to know the LiveKit name, or are you happy being the thing underneath everyone else's product?" If "happy underneath": it's about buyers, credibility and showing what the tech does. If "we want to be known": content and digital start to matter.]*

**6. Measuring success**

> "When you make a marketing bet, how do you decide whether it worked? Pipeline, sign-ups, something else?"

*[Follow-up: "Any event or sponsorship you'd point to as a good one?" Write down what they measure; the ROI answer in section 9 gets agreed upfront against it.]*

**7. Formula 1**

> "And how much do you follow Formula 1? Anyone on the team who's a fan?"

*[If little: keep it simple and use section 5. If a fan: ask which team, but don't read anything into it yet.]*

**8. Decision, budget and timing**

> "If something here made sense, who else would need to be in the conversation? And is there a budget cycle or a rough range we should know about, or is that too early?"

*[If there's no budget: "That's fine. Most brands we talk to don't have an F1 line in the budget. The point of the next step is to see if there's a case worth making." Then move to section 10.]*

## 5. If they ask: "Why are brands like us in Formula 1?"

**Cisco Webex at McLaren (closest comparable; the one the email used)**

- **Who and what:** Webex became McLaren's Official Collaboration Partner in February 2021, with branding on the car, running the team's day-to-day collaboration and powering McLaren Slipstream, a live behind-the-scenes stream for the team's partners. It grew into networking and security, and in July 2026 Cisco extended into AI observability, with Splunk's McLaren relationship brought under Cisco.
- **Why they're in:** proof for buyers. Cisco's SVP of Global Revenue, Field and Partner Marketing said "there is no more powerful proof point to demonstrate to our customers" (July 2026), and they announced the extension at an executive event at McLaren's factory with Cisco customers in the room.
- **What it means for LiveKit:** a real-time communications brand whose product does a working job inside a team, used to sell to enterprise buyers. Same shape, much bigger company.

**Atlassian at Williams (grew up selling to developers)**

- **Who and what:** title partner since February 2025, plus Official Technology Partner and Official Collaboration Software partner. Williams called it the biggest partnership in its 48-year history, and the team is adopting Atlassian's tools across the organization.
- **Why they're in:** a company built on developers telling a story about how great teams work. Mike Cannon-Brookes talked about "engineers, developers, commercial teams, pit crews" working together.
- **What it means for LiveKit:** selling to developers is no reason to stay out. The story was how a team works, not a logo. Use it for the story, never the size.

**RUCKUS at Haas (invisible infrastructure, made visible)**

- **Who and what:** RUCKUS provides enterprise wireless that powers the team's operations, with a live showcase in the garage. Since January 2026 it's Haas's Official Networking Partner across trackside, the factories and hospitality, including guest Wi-Fi in the team's hospitality suite. SPORTFIVE ran the grid-wide process.
- **Why they're in:** infrastructure nobody normally sees, shown working at the track in front of B2B buyers.
- **What it means for LiveKit:** LiveKit is plumbing too, and a working role is how plumbing becomes a story. We ran this one, so you can speak to how the process works.

> "What's interesting is that most tech brands in F1 aren't there to sell to fans. Take Cisco and McLaren. Webex runs the team's collaboration and powered a live stream for McLaren's partners, and Cisco calls the team its best proof point for customers. Atlassian grew up selling to developers, put its name on Williams, and the story was how a team works, not a logo. And RUCKUS at Haas, which we ran, is enterprise wireless doing a real job in the garage, so buyers can see it working. So the thread is a product with a real job, a story buyers believe, and a room to tell it in."

## 6. If they ask: "How are similar brands activating?"

> "There are four or five main ways, and most brands mix two or three.
>
> The first is a working role, where the product does a real job. RUCKUS running wireless at Haas, or Webex running collaboration at McLaren.
>
> Then the business side, hospitality and pipeline. Airwallex at McLaren is a good one: during the partnership they grew revenue 50% year on year across EMEA and the Americas, and UK revenue was up 57% from new customers. And it's the right room. 66% of Paddock Club guests are senior executives, CIOs and CTOs included, and passes work all three days, so seven passes can host twenty different guests in one weekend.
>
> Third is content and digital. AWS has been the sport's cloud and machine learning provider since 2018, and fans see that work in the race graphics. And this year Salesforce launched an AI fan companion on F1.com.
>
> Then drivers, which is a smaller, more personal way in.
>
> And last, market by market. For you that's probably the three US races, Miami, Austin and Las Vegas. F1 even runs a business summit in Vegas on the Thursday of race week."

*Ideas for LiveKit (ideas, not proposals):*

- *Idea: a "built live" series.* A voice agent built in public with open code, about something F1 fans want explained (the 2026 rules, a strategy call), shown at a race. Developers get the code; executives get the story.
- *Idea: enterprise hospitality at a US race.* Las Vegas is the obvious first look (closest to San Francisco, and the Business Summit is that week), hosting the CTOs, Chief AI Officers and customer-experience heads in their pipeline (guest list in "Who they sell to").
- *Idea: a developer program around a race weekend.* A hackathon on public F1 data, winners hosted at a race. It plays to the community they already have, and it's a small door.

## 7. If they ask: "What can we do with the team's other partners?"

> "This is the bit people underestimate. Every team has 25 or more partners, and there are more than 350 across the grid. Teams want their partners doing business with each other, so they run partner summits, introductions and business forums on race weekends. Partners co-host hospitality, make content together, and quite often end up buying from each other.
>
> A recent example: when Cisco extended with McLaren in July, they announced it at an executive event at McLaren's factory, with their own customers there and other McLaren partners, Mastercard and Deloitte, in the room too.
>
> And for you there's a nice twist. A few of the names you list as customers are already in the paddock as partners. Oracle with Red Bull, for one, and Salesforce with Formula 1 itself. That doesn't open any doors on its own, but it tells you it's a room your customers already spend time in."

*[Never claim a specific partner would meet, buy or co-activate. Which partners sit at which team is checked at the mapping stage.]*

Who LiveKit would most want to meet (ideas):

- **Enterprise software, cloud and AI partners:** companies building customer-facing AI that may want a voice layer. Potential integration partners as well as buyers.
- **Brands with big customer service operations:** banks and airlines are in the paddock (Barclays at Williams, Etihad at McLaren, Qatar Airways with F1), and companies like these are the ones buying voice agents for support. Their contact-center leaders are LiveKit's enterprise buyers.
- **Connectivity partners:** LiveKit sells phone numbers and connects agents to phone networks, so telecom and networking partners are natural people to meet.

## 8. If they ask: "Where could our product fit in the team?"

*[Ideas to test with the team's technical department, never claims. Never say or imply any team uses or needs LiveKit.]*

- **Fan and digital platforms (most plausible):** a voice agent fans can talk to in the team's app or site (the rules, the race, the driver's day), or live watch-alongs and driver Q&As where fans talk back without lag, in several languages. Role: "Official Real-Time Communications Partner" (the email's term) or "Official Voice AI Partner". ElevenLabs already holds a voice AI seat at Audi for fans and content, so expect a conflict there.
- **Partner and guest experiences:** live behind-the-scenes audio and video for partners and guests who aren't at the track, and a voice concierge for hospitality guests (schedules, directions, languages). This is where Webex and Slipstream sit at McLaren, so expect conflicts there too.
- **Operations (test with the engineers):** low-lag audio and video between the factory and trackside for work that isn't safety-critical; a hands-free voice interface engineers could use to query tools or data in the garage or the simulator; video from cameras or robots in the factory (their "physical AI" line). Role: technical supplier, for example "Official Real-Time Communications Supplier".
- **Poor fits:** design and simulation compute, manufacturing, logistics, e-commerce. And leave the driver-to-pit-wall radio alone: it's safety-critical and governed by the sporting regulations.

> "I'd be careful saying where it fits before a team's engineers have had a look, so take these as ideas. The most obvious one's the fan side, something fans can talk to in the team's app, or live sessions where fans talk back to a driver without the lag. Then partners and guests, live access for the people who can't be at the track. And maybe operations, voice and video links between the factory and the track, or a voice interface for engineers. Whether any of that's real is a question for the technical people, and that's a conversation we'd set up."

## 9. Other questions they may ask

**"What does something like this cost?"**

> "It ranges a lot. Entry-level and supplier positions start in the low single-digit millions a year, official partner tiers sit above that, and driver, content or pure hospitality programs sit below. For a company your size I'd start with the smaller doors and only go bigger if the case is there."

*[Never quote title-deal numbers.]*

**"Why SPORTFIVE? Why not go direct to a team?"**

> "You could. But a team will sell you its own inventory. We worked exclusively with Mercedes and Ferrari for over twelve years and gave that up so we could work brand-first across all eleven. So we can tell you which team fits, or that none does right now. And the rights holders pay us, so it doesn't cost you anything."

**"Which team would fit us? Your email said some teams were looking."**

> "I don't know yet, and I'd be wary of anyone who told you on a first call. What I meant is there are teams we work with where a partner like you could make sense. Whether the seat's free at a given team, and which team fits your buyers and your markets, is what our grid mapping is for. That's what we'd come back with."

**"How would we measure ROI?"**

> "We agree it upfront, before anything's signed. Usually it's a mix: media value, brand tracking with the audience you care about, pipeline you can trace to the program, and what comes out of hospitality, so meetings, deals, renewals. For you I'd guess pipeline and enterprise meetings matter far more than TV numbers."

**"We sell to developers. Does F1 do anything for us?"**

> "Fair question. Two things. First, your buyer isn't only the developer any more. The big deals get signed by CTOs and the people who run customer experience, and F1 fans index at 160 for business decision makers, the highest in sport. Second, developers don't care about logos, they care about what got built. Atlassian grew up on developers and went to Williams with a story about how a team works. So for you it'd be a real build, open code, something a developer looks at and thinks, okay, that's clever. The logo's the least important part."

*[If they push on size ("we're too early for this"): agree it might be, and point to the small doors: one race of hospitality, a developer program, a driver or content deal. "Not yet" is a fine answer.]*

## 10. Closing and next steps

> "This was really useful, thank you. From what I heard, the overlap is [their enterprise push into contact centers and the room of buyers at the US races], and [a live voice story developers would respect].
>
> So here's what I'd suggest. We write a short brief from today, a page or so, and you correct what we got wrong. Then we come back in [two to three weeks] with a few realistic options and honest numbers, and if the answer's 'not yet', I'll say that plainly. None of it costs you anything.
>
> Does that work as a plan? And any questions for me, Bjorn or George before we wrap?
>
> Great. Thanks again, Michelle. I enjoyed this, and I'm looking forward to the next one."

*[Optional, only if it went well: "And if you'd like to see how it works up close, we'd be happy to host you at a race. It's much easier to judge in person." Las Vegas is 19 to 21 November, three weeks out; otherwise Miami next spring. Check availability before offering a date.]*

---

## Prep notes (not spoken)

- **Fill-ins:** contact is Michelle Schroeder, VP Marketing, from the outreach email; LiveKit's own release of 21 May 2026 confirms the title (she was CMO at PolyAI). Confirm she's on the invite and who else joins. The email also listed Brian Blumenfeld (Product and Ecosystem Partnerships), Tom Davies (CRO) and Andrew Lowry (Founding Field Marketing Manager) as alternates. Fill [two to three weeks]. No email addresses or phone numbers in this script.
- **What the outreach said:** "Wave 2 Priority - Emails Ready", #53, B2B group (Drive, re-read 30 October 2026). Pitched an "Official Real-Time Communications Partner" seat ("A few of our Formula 1 teams are looking for..."), with LiveKit a fit "due to its run to the center of voice AI, powering ChatGPT's voice mode". Audience: AI companies, enterprises and developers, "from OpenAI to Salesforce". Market overlap: the January 2026 round, billions of voice calls a year, and the US races (Miami, Austin, Las Vegas). Shared value: the live voice links between driver, pit wall and factory. Reference: Cisco Webex at McLaren, including Slipstream and the July 2026 AI observability extension. It named McLaren, Haas, Audi and Mercedes as teams we work closely with. It used a sector spend figure ($706M, technology, media and telecom) that isn't in the stat bank: don't repeat it on the call. The "looking" line is handled in section 3.
- **Capacity caution, moderate:** a $1B valuation and $100M raised in January, but around 110 to 140 people, revenue undisclosed, and the round pointed at compute, storage and network services (SiliconANGLE). A typical team entry is $3.5M+ a year. Surface budget in the first half, lead with small doors (hospitality at a US race, content, a developer program, a product-plus-cash supplier seat) and never assume big-team money.
- **Compliance:** no standing compliance note triggered (San Francisco HQ; no India, China or Brazil roots found). 911 centers are public bodies, so no government guests at hospitality without a compliance review; gift and ethics rules apply.
- **Defense category check:** not triggered. LiveKit is civilian developer infrastructure. Three names on their customer list touch defense or policing: Skydio (drones), Axon (police technology) and SpaceXAI (part of SpaceX). Keep all three out of spoken lines and build nothing around them.
- **Claims discipline:** attribute LiveKit's numbers (developers, calls, uptime, latency, 911, Fortune 500) to them. Meta, Microsoft and SpaceXAI are named only in their September release. Never say or imply any team uses or needs LiveKit. Don't link LiveKit to F1's Agentforce fan companion: nothing says it's voice or runs on LiveKit. Don't compare LiveKit with ElevenLabs or call them a rival or a partner; we haven't checked the relationship. Claim no category open. The Loophole Labs rollout timing is their plan, not a fact.
- **Category check:** real-time comms and collaboration: Cisco Webex at McLaren (since 2021, extended July 2026). Voice AI: ElevenLabs at Audi (official partner, 29 January 2026, fan engagement and content). Networking: RUCKUS at Haas (January 2026). Adjacent AI and cloud: Oracle (Red Bull), Microsoft with Mercedes (reported January 2026), Google Cloud (McLaren), AWS and Salesforce (series level; Salesforce extended in March 2026), CoreWeave (Aston Martin), CrowdStrike (Mercedes). No real-time media infrastructure partner found at any team (search, 30 October 2026). Map team by team at the recommendations stage.
- **Cost cap:** any in-kind technical supply may count towards the team's cost cap, so check how the team would treat it (verify).
- **Timing:** Austin has already run this year. Las Vegas is 19 to 21 November 2026, with the F1 Business Summit on Thursday 19 November at Caesars Palace (per F1), so any program realistically starts in 2027. F1's 2027 calendar (published 16 September 2026) has Miami on 30 April to 2 May, Austin on 22 to 24 October and Las Vegas on 18 to 20 November (per reports). Say "more than twenty race weekends" aloud.
- **Where sources disagree:** developer counts rise over time (100,000+ in April 2025, 200,000+ per Index in January 2026, 300,000+ on their homepage now); use the homepage figure, attributed. Headcount: Revelio about 109 (March 2026) against about 136 on a June 2026 job listing; some directories still say 34 (stale). 911: their 2025 post says "roughly a quarter" of dispatch centers; a June 2026 podcast listing says about 30% of 911 calls; use the quarter. Revenue: a 2025 estimate of about $3.7M ARR and an unverified social-post claim of $330M for 2026; use neither. One site reports an unannounced $40M "Series C-1" at $1.45B in August 2026; single source, don't use. RUCKUS is "CommScope's" in the stat bank and "a business of Vistance Networks" in its January 2026 release; say "RUCKUS at Haas". Salesforce's F1 deal runs "through 2030" per one report only.
- **Names check:** from the allowed list (verified in September 2026 checks): Atlassian at Williams, Oracle at Red Bull, HP at Ferrari, AWS since 2018, Microsoft with Mercedes, Google Cloud at McLaren. Stat bank case studies: Airwallex at McLaren, RUCKUS at Haas. From the v4 brief: the Reuters piece of 4 May 2026, CoreWeave at Aston Martin, CrowdStrike at Mercedes. Verified 25 October 2026 and re-checked now: Cisco Webex at McLaren (2021 start, Slipstream, July 2026 extension, executive event with Mastercard and Deloitte), Atlassian details, Salesforce and F1 (March 2026), the F1 Business Summit, AWS race graphics. Verified fresh 30 October 2026: ElevenLabs at Audi, RUCKUS's January 2026 Haas deal, Barclays at Williams (3 February 2026), Etihad at McLaren (26 February 2026), Qatar Airways with F1, the 2027 calendar. LiveKit facts checked 30 October 2026; re-verify on call day.
- **Pipeline check:** confirm no live deal in real-time comms or voice AI. Drive search (30 October 2026): LiveKit appears only in the Wave 2 email, the 25 October version of this script, and prospect lists (FOLLOW UP MASTER DOCUMENT, AIML FOLLOW UP, FOLLOW UP.xlsx, CLOUD.xlsx). No other outreach found.
- **Which company:** LiveKit (livekit.io, now also livekit.com), the San Francisco company. Not LiveLike (sports fan engagement), not LiveU (broadcast video) and not "Live kit" (a Japanese live-commerce service). "SpaceXAI" on their customer page is xAI's new name after SpaceX bought it (closed February 2026, renamed July 2026, per reports).
- **New sources (grouped):**
  - LiveKit's own: https://livekit.com/ ; https://livekit.com/customers ; https://livekit.com/pricing ; https://livekit.com/careers ; https://livekit.com/blog ; https://docs.livekit.io/agents/ ; https://livekit.com/blog/livekit-series-c/ ; https://livekit.com/blog/livekits-series-b/ ; https://community.livekit.io/t/introducing-livekit-connectors-voice-agents-where-people-already-talk/1983
  - LiveKit releases and job ads: https://eznewswire.com/newsroom/livekit-chief-revenue-officer-enterprise-growth ; https://fortune.com/press-releases/livekit-acquires-loophole-labs-ai-agent-infrastructure-2026-09-24/ ; https://careers.redpoint.com/companies/livekit/jobs/72336560-director-of-revenue-marketing
  - Reporting and investors: https://techcrunch.com/2026/01/22/voice-ai-engine-and-openai-partner-livekit-hits-1b-valuation/ ; https://siliconangle.com/2026/01/22/livekit-raises-100m-1b-valuation-scale-real-time-ai-media-platform/ ; https://www.indexventures.com/perspectives/see-hear-speak-investing-in-livekit-and-the-future-of-realtime-applications/ ; https://www.pymnts.com/news/investment-tracker/2026/livekit-raises-100-million-dollars-voice-ai-developer-platform/ ; https://www.reveliolabs.com/companies/livekit/employees
  - Customer context: https://seekingalpha.com/news/4497865-axon-to-acquire-emergency-communications-platform-prepared ; https://gigazine.net/gsc_news/en/20260707-xai-change-spacexai
  - F1 category and comparables: https://contenthub.audif1.com/en/releases/elevenlabs-named-official-partner-of-audi-revolut-f1-team-97 ; https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2026/m07/accelerating-the-future-a-new-era-of-ai-powered-performance.html ; https://newsroom.cisco.com/c/r/newsroom/en/us/a/y2021/m02/tbd-jimin.html ; https://www.sportsvideo.org/2026/07/07/cisco-and-mclaren-mastercard-formula-1-team-extend-technology-partnership/ ; https://www.businesswire.com/news/home/20260121228711/en/RUCKUS-Networks-Announces-Official-Partnership-with-TGR-Haas-F1-Team/ ; https://www.silicon.co.uk/press-release/williams-and-atlassian-announce-title-partnership-to-form-atlassian-williams-racing ; https://www.mercedesamgf1.com/news/mercedes-announces-global-partnership-with-crowdstrike ; https://aws.amazon.com/sports/f1/ ; https://www.salesforce.com/news/press-releases/2026/03/03/formula-1-agentforce-to-grow-fan-connection/
  - Reuters, 4 May 2026 (tech the top team spending category; eight new AI partnerships in six months): https://whbl.com/2026/05/04/motor-racing-as-formula-one-evolves-ai-becomes-part-of-the-race/ ; https://www.timeslive.co.za/motoring/2026-05-04-as-formula-one-evolves-ai-is-fast-becoming-a-crucial-part-of-the-race/
  - Paddock partners in their customers' sectors: https://www.williamsf1.com/articles/d9df5ea8-6286-4cf8-85da-e6bd96ef7e2e/barclays-official-banking-partner ; https://www.mclaren.com/racing/latest-news/2026/mclaren-racing-announces-etihad-airways-as-an-official-partner/ ; https://www.qatarairways.com/en/press-releases/2023/February/qatar-airways-formula1-partnership.html
  - Calendar and events: https://www.formula1.com/en/latest/article/f1-business-summit-adds-haas-boss-komatsu-gordon-ramsay-and-russell-wilson.7bjK395TdRilEl7AorqYMG ; https://www.mclaren.com/racing/formula-1/2026/2027-calendar-announced/
