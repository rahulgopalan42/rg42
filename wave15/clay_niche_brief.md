# Clay niche keyword pull (Wave 15 top-up for thin tech tabs)

Clay often labels niche tech firms as plain "Software" or "IT Services", so industry searches miss them. Find them by
what they sell. Today is 14 October 2026. The user has asked for this.

1. Load tools: ToolSearch "select:mcp__Clay__search-companies,mcp__Clay__load-more-search-results".
2. For each topic below run:
   select from companies where products_and_services is_similar_to (<phrases>) and company_size in ("51-200",
   "201-500","501-1,000","1,001-5,000","5,001-10,000","10,001+") and annual_revenue in ("75M-200M","200M-500M",
   "500M-1B","1B-10B","10B-100B","100B-1T")
   then a second search with the same topic but, instead of the revenue filter, a funding filter on
   total_funding_amount_range_usd for USD 100M+ (find the exact bucket values; e.g. "$100M - $250M", "$250M+").
   Page each to the end (cap 60 pages per search).
   Topics (phrases): supercomputing ("supercomputer","high performance computing HPC","GPU servers");
   storage ("enterprise data storage","flash storage arrays","backup and data protection");
   observability ("observability platform","application performance monitoring","log analytics");
   EDA ("electronic design automation","chip design software","semiconductor IP");
   ERP & procurement ("ERP software","procurement software","spend management");
   AI agents ("AI agents","AI assistant platform","conversational AI");
   AI data services ("AI training data","data labeling","AI model evaluation");
   edge & CDN ("content delivery network","edge computing platform");
   robotics AI ("humanoid robots","robot foundation models","autonomous mobile robots");
   devtools ("developer tools","API platform","integration platform iPaaS");
   UCaaS & CPaaS ("unified communications","CPaaS messaging API","contact center software");
   AI cloud ("GPU cloud","AI infrastructure cloud","data platform");
   cyber ("cybersecurity platform","identity security","endpoint security");
   chips & semi equipment ("semiconductor company","chip maker","semiconductor equipment");
   photonics ("photonics","lasers","optical components");
   test & measurement ("test and measurement instruments","electronic test equipment");
   industrial gases ("industrial gases","hydrogen supply"); TIC ("testing inspection certification").
3. Append EVERY company to /home/user/rg42/wave15/clay_niche.tsv (header first): name, domain, country, locality,
   type, size, employee_count, annual_revenue, industry, linkedin_url, search (= "N|<topic>|rev" or "N|<topic>|fund").
   Strip tabs/newlines/"|" from values. Append after each page with python3 -I. Helper files only in
   /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/niche/.
4. Report ONLY: rows per topic, any filter errors. Under 80 words.
