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
  ["Formula 1", ["American Express", "Santander", "Standard Chartered", "Crypto.com"]],
  ["Alpine", ["eToro", "Mobilize Financial Services", "BlockDAG"]],
  ["Aston Martin", ["Coinbase", "CoinPayments", "Pepperstone", "Public"]],
  ["Audi", ["Revolut", "Nexo"]],
  ["Cadillac", []],
  ["Ferrari", ["UniCredit", "BingX"]],
  ["Haas", ["IC Markets", "Zoomex"]],
  ["McLaren", ["Mastercard", "Airwallex", "OKX", "FxPro"]],
  ["Mercedes", ["Stripe", "Nu", "Nasdaq"]],
  ["Racing Bulls", ["Visa", "Cash App", "XMTrading"]],
  ["Red Bull Racing", ["Visa", "Carlyle", "AvaTrade", "Gate"]],
  ["Williams", ["Barclays", "BNY", "Nuveen", "Stephens", "Kraken"]],
];
const UNIQUE = new Set(BRANDS.flatMap(([, b]) => b)).size; // 35 (Visa partners two teams)
const TEAMS_WITH = BRANDS.filter(([n, b]) => n !== "Formula 1" && b.length).length; // 10 of 11

const NOTES = [
  `${UNIQUE} financial services brands partner Formula 1 or the teams (Visa partners two teams): payments, banking, asset management, trading and crypto. Every team except Cadillac has at least one (${TEAMS_WITH} of 11). Stripe (Mercedes) and Airwallex (McLaren) are the two from the competitive landscape on the previous slide.`,
  "Formula 1: American Express, Americas payments partner (Oct 2023), global (Oct 2024); Santander, Official Retail Banking Partner (Sep 2024); Standard Chartered, Official Partner (Jan 2026); Crypto.com, extended to 2030 (Dec 2024).",
  "Teams: Mercedes and Stripe (20 Oct 2026), Nu (20 Jan 2026), Nasdaq (Apr 2025). McLaren and Mastercard (title from 2026), Airwallex (extended Oct 2026), OKX (to end-2026), FxPro (25 Feb 2026). Audi and Revolut (title from 2026), Nexo (16 Jan 2026). Visa, title partner of Racing Bulls with Cash App and on the Red Bull Racing car (19 Feb 2026); Racing Bulls and XMTrading (2026). Red Bull Racing and Carlyle (exclusive investment management partner, Sep 2025), AvaTrade (multi-year from 2025), Gate (2025). Aston Martin and Coinbase (Feb 2025), CoinPayments (Dec 2025), Pepperstone (Jun 2025), Public (multi-year from Apr 2025). Ferrari and UniCredit (2025), BingX (2026). Williams and Barclays (Feb 2026), BNY (30 Jan 2026), Nuveen (22 Jan 2026), Stephens (Official Investment Banking Partner since 2023), Kraken (renewed Jan 2026). Alpine and eToro (15 Jan 2026), Mobilize Financial Services (2025, continuing), BlockDAG (Sep 2025, multi-year). Haas and IC Markets (Official FX Trading Partner, Dec 2025, multi-year), Zoomex (renewed for 2026).",
  "Not counted: Mercado Libre (Alpine; marketplace), Aleph (Audi; digital advertising), Allwyn (F1; lottery), Nuvei (Mercedes, 2023 multi-year deal; current status not confirmed). Ended before 2026: MoneyGram (Haas), Hantec Markets (Haas), Santander at Ferrari and Williams, Bybit (Red Bull Racing).",
].join("\n");

async function build() {
  await D.defineLayouts();
  pres.addSection({ title: "Financial services landscape" });
  const s = content("CONTENT", "Financial services landscape", null, "Financial services landscape",
    t(`**${UNIQUE} financial services brands** partner F1 and ${TEAMS_WITH} of its 11 teams`), "", NOTES);

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
