# Clay pull for the Wave 14 new sectors (Wave 15 top-up)

Find companies in the sectors Wave 14 added outside the 56 master tabs. Search by what they sell, because Clay's
industry labels miss many of them. Today is 14 October 2026. The user has asked for this.

1. Load tools: ToolSearch "select:mcp__Clay__search-companies,mcp__Clay__load-more-search-results".
2. For each topic in YOUR PART (given in your task) run two searches:
   rev:  select from companies where products_and_services is_similar_to (<phrases>) and company_size in ("51-200",
         "201-500","501-1,000","1,001-5,000","5,001-10,000","10,001+") and annual_revenue in ("75M-200M",
         "200M-500M","500M-1B","1B-10B","10B-100B","100B-1T")
   fund: same, but replace the revenue filter with total_funding_amount_range_usd in the USD 100M+ buckets
         (find the exact bucket values once; e.g. "$100M - $250M", "$250M+").
   Page each to the end (cap 80 pages per search). If a rev search hits the cap, re-run it split by company_size.
3. Append EVERY company to /home/user/rg42/wave15/clay_w14_<part>.tsv (header first): name, domain, country,
   locality, type, size, employee_count, annual_revenue, industry, linkedin_url, search
   (= "W14|<code>|rev" or "W14|<code>|fund"). Strip tabs/newlines/"|" from values. Append after each page with
   python3 -I. Helper files only in
   /tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w14_<part>/.
4. Report ONLY: rows per topic, any filter errors. Under 80 words.

PART A
X01 ("asset management","private equity firm","proprietary trading firm","hedge fund")
X03 ("contract development and manufacturing CDMO","contract research organization CRO","life science tools")
X07 ("aerospace components supplier","aircraft parts manufacturer","aircraft interiors")
X08 ("sporting goods brand","fitness equipment","outdoor gear")
X10 ("battery manufacturer","electric vehicle charging","battery materials")
X11 ("engineering consultancy","infrastructure design consultancy")
X12 ("rail rolling stock","transit operator","toll road operator")
X13 ("industrial distribution","MRO supplies distributor","electrical distributor")
X14 ("warehouse automation","intralogistics systems","material handling equipment")
X15 ("consumer electronics brand","headphones and audio","smart home devices")
X16 ("specialty chemicals","coatings and paints","adhesives and sealants")
X17 ("private 5G networks","telecom equipment","radio access network")
X18 ("quantum computing","quantum sensing","quantum software")
X19 ("pet food","pet care products","veterinary services")
X20 ("sports nutrition","recovery and wellness devices","fitness clubs")

PART B
X21 ("luxury watches","fine jewellery","jewelry brand")
X23 ("gaming peripherals","gaming hardware","esports equipment")
X24 ("ticketing platform","live events promoter","experiential events")
X25 ("wealth management","private banking","family office services")
X26 ("insurance broker","reinsurance")
X27 ("payroll software","employer of record EOR","global HR platform")
X28 ("franchise group","multi-brand franchisor","restaurant franchise operator")
X29 ("water technology","desalination","water treatment solutions")
X30 ("waste management","recycling","circular economy materials")
X31 ("agritech","crop inputs seeds and fertilizer","precision agriculture")
X32 ("mining services","mining equipment","drilling services")
X34 ("private aviation","business jets","yacht builder superyacht")
X35 ("sports technology","fan engagement platform","sports data and analytics")
X36 ("creator economy platform","influencer marketing platform","social commerce")
NEW-AUC ("auction house","collectibles marketplace","trading cards")
NEW-EDU ("education technology","school operator","online learning platform")
NEW-MED ("media and publishing","news publisher","streaming platform")
NEW-SOC ("social network","messaging app","dating app")
X38-41 regional champions: run rev searches only, adding a description filter instead of a country filter:
  ("conglomerate","diversified group") with industry in ("Holding Companies","Retail","Consumer Goods",
  "Food and Beverage Manufacturing") — tag search "W14|X38-41|rev".
