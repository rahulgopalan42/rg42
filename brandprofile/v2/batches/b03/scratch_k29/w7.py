import sys; sys.path.insert(0,"scratch_k29")
from rec import *
Q="https://en.wikipedia.org/wiki/Qi_Card"
W("main",name="Qi Card (International Smart Card)",website="qi.iq",aliases=["International Smart Card","ISC","Qi Card"],hq_city="Baghdad",hq_country="Iraq",sector="Financial Services & Payments",subsector="national card and payments network",
 desc="Iraq's national debit and payment card network, a public-private venture set up with Rafidain and Rasheed banks, serving about 9 million cardholders.",
 products="debit and prepaid cards, salary and pension payments, POS acquiring, offline smart-card payments",model="Hybrid",customers="about 9 million cardholders; government salary and pension payees",
 ownership_type="joint venture",parent_immediate="International Smart Card",parent_ultimate="Rafidain Bank and Rasheed Bank (state) with Iraqi Electronic Payment System; stakes not stated",parent_listed="requires verification",
 employees=3500,markets="Iraq",reach="Domestic",route="A",
 fin=[{"metric":"revenue","value_orig":"USD 1.2bn","usd_m":1200,"period":"FY2021","published":"","kind":"reported","source":Q}],qualifying_metric="revenue (2021, older than three years)",
 signals=[],fit="10001221",fit_rationale="Iraq's dominant payments network with 9 million cardholders; F1 could support a card-brand push and Gulf positioning, but operations are domestic and governance is opaque.",
 category_conflict="potential: Visa and Mastercard-type payment partners in F1",compliance="state-linked public-private venture; ownership and governance need verification",
 access=("unknown","no","complex","Chairman, CEO, marketing director"),signals_checked="no",outstanding="company site 404; current financials; ownership split; whether any shares trade",sources=[Q],conf="low",discovery_source="https://en.wikipedia.org/wiki/List_of_companies_of_Iraq")
I="https://en.wikipedia.org/wiki/Israel_Electric_Corporation"
W("main",name="Israel Electric Corporation",website="iec.co.il",aliases=["IEC"],hq_city="Haifa",hq_country="Israel",sector="Utilities & Renewable Energy",subsector="national electricity utility",
 desc="State-owned Israeli electricity utility generating and distributing most of the country's power from about 50 power station sites.",products="electricity generation, transmission and distribution",model="Hybrid",customers="Israeli households and businesses",
 ownership_type="state-owned",parent_ultimate="State of Israel (about 99.85%)",parent_listed="state",employees=12676,markets="Israel",reach="Domestic",route="A",
 fin=[{"metric":"revenue","value_orig":"ILS 27.7bn","usd_m":None,"period":"FY2013","published":"","kind":"reported","source":I}],qualifying_metric="revenue (2013 figure, old; ILS not in fixed rate list) and documented state ownership",
 signals=[],fit="00000100",fit_rationale="Monopoly-like domestic utility with no international market or consumer marketing need; F1 relevance is minimal despite scale.",
 access=("no","no","complex","CEO, spokesperson"),signals_checked="no",outstanding="recent financials; news page not opened",sources=[I],conf="medium",discovery_source=I)
