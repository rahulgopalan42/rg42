# Add-on brief: Chinese listed mid-caps (read research_brief.md first; the same rules and output format apply)

Why this works: our earlier market-cap listing held only ~384 Chinese companies over USD 1B, but ~2,500 China-listed
companies (Shanghai, Shenzhen, STAR, ChiNext, Beijing; Hong Kong) are worth USD 1B+. Many mid-caps (USD 1-8B) are NEW.
Sample of NEW names we already saw: Suofeiya (Sofia home), Mengtian Home, Yanjin Puzi, Hengshui Laobaigan, Xinjiang
Yilite, Chengde Lolo, Hebei Yangyuan Zhihui, Zhejiang Li Zi Yuan, Sinomine, Ronbay, Jiugui Liquor, Hengshun Vinegar.

Method (keep WebSearch use LOW - you have a limited search budget; prefer WebFetch on known URLs):
1. From your own knowledge, list 150-250 China-listed companies in your sector list (CSI 500 / CSI 1000 / ChiNext /
   STAR / Hang Seng Composite mid-caps) with their English names, pinyin names and stock codes.
2. Run them ALL through the checker in batches of 40-60 (English name, pinyin name and brand name each as a separate
   entry, e.g. "Suofeiya Home Collection|" "Sofia Home|"). Keep only companies where EVERY version is NEW.
3. Verify the market cap for each NEW one by fetching its stockanalysis.com page directly:
   Shanghai https://stockanalysis.com/quote/sha/<6-digit code>/ ; Shenzhen https://stockanalysis.com/quote/she/<code>/ ;
   Hong Kong https://stockanalysis.com/quote/hkg/<code>/  (fall back to one WebSearch "<code> market cap" if needed).
   Market cap must be >= USD 1B. Convert CNY at 7.1 per USD and HKD at 7.8; put the local figure, the page and the
   date shown in source_note; source_url = the page you fetched. basis = "market cap", listed = true, ticker = code.
4. "what": what the company makes/sells, its main consumer brands (very important for sponsorship), scale (revenue).
   Skip subsidiaries of a group whose listed parent is EXCLUDED, state holding shells, banks' asset-management arms.
Prefer consumer-facing brands, then companies selling internationally.
