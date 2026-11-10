// Financial services landscape in F1 (as at 10 Nov 2026): one slide for the Final deck, brand names by team only.
// Usage: node build_payments_landscape.js "Adyen x F1 - Payments landscape.pptx"
// Set in Calibri to match the Final deck PDF. Every deal was checked against the team's, the partner's or
// Formula 1's own announcement (sources in the speaker notes).
const D = require("./build_deck.js");
const { pres, C, L, R, CW, t, card, content } = D;

const OUT = process.argv[2] || "Adyen x F1 - Payments landscape.pptx";
pres.title = "Adyen x Formula 1: financial services landscape";
pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
D.THEME.headFontFace = "Calibri";
D.THEME.bodyFontFace = "Calibri";
D.SHORT_SOURCE["Financial services landscape"] = "Source: Formula 1; teams; partner announcements (Nov 2026).";

// Formula 1 first, then the teams A–Z; brands in the order of the deal's prominence (title partners first)
const BRANDS = [
  ["Formula 1", ["American Express", "Santander", "Standard Chartered", "Crypto.com", "Marsh"]],
  ["Alpine", ["eToro", "Mobilize Financial Services"]],
  ["Aston Martin", ["Coinbase", "CoinPayments", "Pepperstone", "Public"]],
  ["Audi", ["Revolut", "Nexo", "Libertex"]],
  ["Cadillac", []],
  ["Ferrari", ["UniCredit", "Aon", "ZCG", "Vantage Markets", "BingX"]],
  ["Haas", ["Bradesco", "IC Markets", "Orion180", "Zoomex"]],
  ["McLaren", ["Mastercard", "Airwallex", "Edward Jones", "OKX", "FxPro"]],
  ["Mercedes", ["Stripe", "UBS", "Nu", "Nasdaq"]],
  ["Racing Bulls", ["Visa", "Cash App", "XMTrading"]],
  ["Red Bull Racing", ["Visa", "Carlyle", "AvaTrade", "Gate"]],
  ["Williams", ["Barclays", "BNY", "Nuveen", "Stephens", "Kraken"]],
];
const UNIQUE = new Set(BRANDS.flatMap(([, b]) => b)).size; // 43 (Visa partners two teams)
const TEAMS_WITH = BRANDS.filter(([n, b]) => n !== "Formula 1" && b.length).length; // 10 of 11

const NOTES = [
  `${UNIQUE} banking, finance and insurance brands partner Formula 1 or the teams (Visa partners two teams): banks, payments, wealth and asset management, investment banking, insurance, trading and crypto. Every team except Cadillac has at least one (${TEAMS_WITH} of 11). Stripe (Mercedes) and Airwallex (McLaren) are the two from the competitive landscape on the previous slide.`,
  "Checked against the official partner pages of Mercedes, Red Bull Racing, Racing Bulls, Aston Martin, Alpine, Williams, Haas and Audi (10 Nov 2026), and against team, partner or Formula 1 announcements for Ferrari, McLaren and the series.",
  "Formula 1: American Express (Americas 2023, global 2024); Santander, Official Retail Banking Partner (Sep 2024); Standard Chartered, wealth management and corporate and investment banking (Jan 2026); Crypto.com (to 2030); Marsh, Official Risk and Insurance Brokering Partner (28 Apr 2026).",
  "Ferrari: UniCredit (2025), Aon (Official Partner from Monza 2025), ZCG (extended through 2026), Vantage Markets (multi-year from 2025), BingX (2026). McLaren: Mastercard (title from 2026), Airwallex (extended Oct 2026), Edward Jones (Official Private Wealth Management Partner, 29 Sep 2026), OKX (to end-2026), FxPro (25 Feb 2026). Haas: Bradesco (Official Banking Partner, Nov 2026), IC Markets (Dec 2025), Orion180 (insurance, multi-year from 2024), Zoomex (2026). Audi: Revolut (title), Nexo (Jan 2026), Libertex (3 Mar 2026). Mercedes: Stripe (20 Oct 2026), UBS, Nu (Jan 2026), Nasdaq (2025). Williams: Barclays, BNY, Nuveen (2026), Stephens (since 2023), Kraken. Red Bull Racing: Visa, Carlyle (Sep 2025), AvaTrade (2025), Gate (2025). Racing Bulls: Visa, Cash App, XMTrading. Aston Martin: Coinbase, CoinPayments, Pepperstone, Public. Alpine: eToro (2026), Mobilize Financial Services.",
  "Not counted: Goldman Sachs (McLaren partner from 2022; not confirmed by McLaren for 2026), Nuvei (left Mercedes), BlockDAG (no longer on Alpine's partner list), Emburse (Haas) and Perk (Audi) (spend-management software), Aleph (Audi; media), JCB (Aston Martin; construction equipment), Allwyn (lottery), PwC and Deloitte (professional services), Mercado Libre (marketplace).",
].join("\n");

async function build() {
  await D.defineLayouts();
  pres.addSection({ title: "Financial services landscape" });
  const s = content("CONTENT", "Financial services landscape", null, "Financial services landscape",
    t(`**${UNIQUE} banking, finance and insurance brands** partner F1 and ${TEAMS_WITH} of its 11 teams`), "", NOTES);

  const cols = 4, gap = 0.16, y0 = 1.6, th = 1.62;
  const tw = (CW - gap * (cols - 1)) / cols;
  BRANDS.forEach(([team, brands], i) => {
    const x = L + (i % cols) * (tw + gap), y = y0 + Math.floor(i / cols) * (th + gap);
    const series = team === "Formula 1";
    card(s, x, y, tw, th, series ? C.text1 : C.background2, team);
    s.addText(team.toUpperCase(), { x: x + 0.25, y: y + 0.14, w: tw - 0.5, h: 0.26, fontSize: 10.5, bold: true, charSpacing: 1.2,
      color: series ? C.accent1 : C.accent2, margin: 0, isTextBox: true, valign: "top" });
    const runs = brands.length
      ? brands.map((b, k) => ({ text: b, options: { bold: true, fontSize: 13, color: series ? C.background1 : C.text1,
        breakLine: k < brands.length - 1 } }))
      : [{ text: "None announced", options: { italic: true, fontSize: 12, color: C.accent3 } }];
    s.addText(runs, { x: x + 0.25, y: y + 0.42, w: tw - 0.5, h: th - 0.5, margin: 0, isTextBox: true, valign: "top",
      paraSpaceAfter: 0 });
  });

  await pres.writeFile({ fileName: OUT });
  await D.applyTheme(OUT, D.THEME);
  console.log("wrote", OUT, `(${UNIQUE} brands, ${TEAMS_WITH} of 11 teams)`);
}

build().catch((e) => { console.error(e); process.exit(1); });
