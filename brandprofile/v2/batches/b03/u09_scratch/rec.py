import json,os
B='/home/user/rg42/brandprofile/v2/batches/b03/'
MAIN=B+'u09_pe_portfolio_b.jsonl'; WATCH=B+'watch_u09_pe_portfolio_b.jsonl'
def R(name,website,hq_city,hq_country,sector,subsector,desc,products,model,customers,pe,parent_imm,src_list,route,fin,qual,fit,rat,f1m,
      aliases=(),employees=None,countries=None,sites='',markets='',exp='',reach='International',alt=(),exc='',prof='unknown',profb='',
      distress='',spons=(),signals=(),overlap='',conflict='none found',owner_led='unknown',mkt='no',structure='mid',roles='CEO; CMO / Head of Marketing',
      outstanding='',conf='medium',disc_src='',sig_checked='yes',minority='',ptype='private equity-backed',watch=False,parent_backing='',mauto='unknown',mautob=''):
    r={"name":name,"website":website,"aliases":list(aliases),"hq_city":hq_city,"hq_country":hq_country,"sector":sector,"subsector":subsector,
       "desc":desc,"products":products,"model":model,"customers":customers,"ownership_type":ptype,"parent_immediate":parent_imm,
       "parent_ultimate":pe,"parent_listed":"private","pe_swf_owner":pe,"minority_investors":minority,"marketing_autonomy":mauto,
       "marketing_autonomy_basis":mautob,"parent_backing":parent_backing,"employees":employees,"countries":countries,"stores_or_sites":sites,
       "markets":markets,"expansion_markets":exp,"reach":reach,"route":"none" if watch else route,"fin":list(fin),"qualifying_metric":qual,
       "alt_indicators":list(alt),"exception_note":exc,"profitability":prof,"profitability_basis":profb,"distress":distress,
       "sponsorships":list(spons),"signals":list(signals),"fit":dict(zip(["b2b","ecosystem","technical","hospitality","geography","brand","consumer","category"],fit)),
       "fit_rationale":rat,"customer_overlap":overlap,"category_conflict":conflict,"f1_markets":f1m,
       "access":{"owner_led":owner_led,"marketing_head_identified":mkt,"structure":structure,"roles":roles},"compliance":"",
       "outstanding":outstanding,"sources":list(src_list),"verified":"2026-11-28","conf":conf,"discovered_via":"Independent web research",
       "discovery_source":disc_src,"signals_checked":sig_checked}
    with open(WATCH if watch else MAIN,'a') as f: f.write(json.dumps(r,ensure_ascii=False)+'\n')
    print('wrote',name,'WATCH' if watch else 'MAIN')
def F(metric,value,usd,period,source,kind='reported',published=''):
    return {"metric":metric,"value_orig":value,"usd_m":usd,"period":period,"published":published,"kind":kind,"source":source}
def S(cat,what,date,source,status='confirmed'):
    return {"category":cat,"what":what,"date":date,"status":status,"source":source}
def A(ind,ev,src): return {"indicator":ind,"evidence":ev,"source":src}
