"""Convert saved Apollo company-search tool results into parents/apollo/<prefix>_NNN.json rows
[id, name, primary_domain, linkedin_url, founded_year, publicly_traded_exchange, owner_name, owner_website, revenue_printed, sic0, naics0]
Usage: apollo_convert.py <result_file> <page_number> [prefix]   (prefix default 'page'; use 'rev' for revenue pulls)"""
import json, sys, os
src, page = sys.argv[1], int(sys.argv[2]); prefix = sys.argv[3] if len(sys.argv) > 3 else 'page'
txt = open(src, errors='ignore').read()
start = txt.find('{'); d = json.loads(txt[start:txt.rfind('}') + 1])
rows = []
for o in d.get('organizations', []) + d.get('accounts', []):
    own = o.get('owned_by_organization') or {}
    rows.append([o.get('id') or o.get('organization_id'), o.get('name', ''), o.get('primary_domain') or o.get('domain') or '', o.get('linkedin_url') or '',
                 o.get('founded_year'), o.get('publicly_traded_exchange') or '', own.get('name') or '', own.get('website_url') or '',
                 o.get('organization_revenue_printed') or '', (o.get('sic_codes') or [''])[0], (o.get('naics_codes') or [''])[0]])
out = f'/home/user/rg42/parents/apollo/{prefix}_{page:03d}.json'
json.dump(rows, open(out, 'w'), ensure_ascii=False)
pg = d.get('pagination', {})
print(out, len(rows), 'rows | total_entries', pg.get('total_entries'), '| pages', pg.get('total_pages'))
