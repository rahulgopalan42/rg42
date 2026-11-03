"""Wave 16 step 1a: load the 13 Clay 'Friday export' CSVs into one table (pandas)."""
import glob, os, re
import pandas as pd
S = '/tmp/claude-0/-home-user-rg42/f658b5c3-a5ae-5398-b208-f286520b1971/scratchpad/w16'
frames = []
for f in sorted(glob.glob(f'{S}/new/*.csv')):
    df = pd.read_csv(f, dtype=str, keep_default_na=False)
    title = df.columns[0]
    df = df.drop(columns=[title])
    df['source_csv'] = os.path.basename(f)
    df['clay_search'] = title
    frames.append(df)
    print(os.path.basename(f), len(df), '|', title)
new = pd.concat(frames, ignore_index=True)
new.columns = [c.strip().lower().replace(' ', '_') for c in new.columns]
new.to_parquet(f'{S}/new_all.parquet') if False else new.to_pickle(f'{S}/new_all.pkl')
print('total rows', len(new), 'unique domains', new['domain'].str.lower().str.strip().replace('', pd.NA).nunique())
print(new['type'].value_counts().head(10).to_dict())
