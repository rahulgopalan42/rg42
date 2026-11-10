// Payments landscape in F1 (as at 10 Nov 2026): four slides in the Chairman deck's style.
// Usage: node build_payments_landscape.js "Adyen x F1 - Payments landscape.pptx"
// Every deal below was checked against the team's, the partner's or Formula 1's own announcement (sources in the notes).
const D = require("./build_deck.js");
const { pres, C, S, L, R, CW, t, card, label, content, iconDot } = D;

const OUT = process.argv[2] || "Adyen x F1 - Payments landscape.pptx";
pres.title = "Adyen x Formula 1: payments landscape";
const SRC = "Source: Formula 1; teams; partner announcements (to 10 Nov 2026).";
["Payments landscape", "Payments landscape · Networks and platforms", "Payments landscape · Banks, trading and crypto",
  "Payments landscape · What it means"].forEach((k) => { D.SHORT_SOURCE[k] = SRC; });
const TRACK = 2; // "Adyen in F1"

// ------------------------------------------------------------------ data
// rights holder, card networks, payments platforms, banks, trading & investing, crypto
const MAP = [
  ["Formula 1 (series)", "American Express", "", "Santander\nStandard Chartered", "", "Crypto.com"],
  ["Alpine", "", "", "", "eToro", ""],
  ["Aston Martin", "", "CoinPayments*", "", "Pepperstone", "Coinbase"],
  ["Audi", "", "Revolut (title)", "", "", "Nexo"],
  ["Cadillac", "", "", "", "", ""],
  ["Ferrari", "", "", "UniCredit", "", "BingX"],
  ["Haas", "", "", "", "", "Zoomex"],
  ["McLaren", "Mastercard (title)", "Airwallex", "", "FxPro", "OKX"],
  ["Mercedes", "", "Stripe", "Nu", "Nasdaq", ""],
  ["Racing Bulls", "Visa + Cash App (title)", "", "", "XMTrading", ""],
  ["Red Bull Racing", "Visa", "", "", "", "Gate"],
  ["Williams", "", "", "Barclays\nBNY", "", "Kraken"],
];

const NETWORKS = [
  ["American Express", "Formula 1 · Official Payments Partner",
    "Americas from 2023, global from 2025. Card-member access and experiences at 20+ races; also F1 Academy."],
  ["Visa, with Cash App", "Racing Bulls title partner · Red Bull Racing",
    "Title partner since 2024; renewed in February 2026 to 2030. Visa added to the Red Bull Racing car in 2026."],
  ["Mastercard", "McLaren · title partner (McLaren Mastercard F1 Team)",
    "Partner since 2024, title partner from 2026. Activations run under the name 'Team Priceless'."],
];
const PLATFORMS = [
  ["Stripe", "Mercedes · Official Global Payments Partner", true,
    "Announced 20 Oct 2026, multi-year. Team retail at races first (late 2026), then merchandise and international transactions. On the car from 2027."],
  ["Airwallex", "McLaren · supplier payments", true,
    "Partner since 2024; Official AI Finance Partner from January 2027. Pays suppliers in local currencies across race locations."],
  ["Revolut", "Audi · title partner (Audi Revolut F1 Team)", false,
    "From 2026, multi-year. Revolut Business in the team's financial operations; checkout for team merchandise."],
  ["CoinPayments", "Aston Martin · global partner", false,
    "Since December 2025. Exploring digital-asset payments for customer purchases (May 2026)."],
];
const BANKS = [
  ["Santander", "F1 · Official Retail Banking Partner, from 2025"],
  ["Standard Chartered", "F1 · wealth, corporate and investment banking, from 2026"],
  ["UniCredit", "Ferrari · premium partner, from 2025"],
  ["Barclays", "Williams · Official Banking Partner and main corporate bank, from 2026"],
  ["BNY", "Williams · Official Institutional Banking Partner, from 2026"],
  ["Nu", "Mercedes · team partner, from 2026"],
];
const TRADING = [
  ["Nasdaq", "Mercedes · brand partner, from 2025"],
  ["FxPro", "McLaren · official partner, since 2018"],
  ["XMTrading", "Racing Bulls · FX trading partner, since 2023"],
  ["Pepperstone", "Aston Martin · trading partner, from 2025"],
  ["eToro", "Alpine · trading and investment partner, from 2026"],
];
const CRYPTO = [
  ["Crypto.com", "F1 · global partner to 2030; Miami GP title"],
  ["OKX", "McLaren · since 2022, current deal to end-2026"],
  ["Gate", "Red Bull Racing · exclusive exchange, from 2025"],
  ["BingX", "Ferrari · team partner, from 2026"],
  ["Coinbase", "Aston Martin · exclusive crypto partner, from 2025"],
  ["Kraken", "Williams · since 2023, renewed 2026"],
  ["Nexo", "Audi · digital asset partner, from 2026"],
  ["Zoomex", "Haas · exchange partner, since 2025, renewed 2026"],
];
// teams by payments seat (a partner inside the team's payments: commerce, payouts or finance operations)
const TEAMS = [
  ["Alpine", null, "Route 2"], ["Aston Martin", "CoinPayments*", null], ["Audi", "Revolut", null], ["Cadillac", null, null],
  ["Ferrari", null, "Route 3"], ["Haas", null, null], ["McLaren", "Airwallex", null], ["Mercedes", "Stripe", null],
  ["Racing Bulls", null, null], ["Red Bull Racing", null, "Route 1 (Max)"], ["Williams", null, null],
];

const SOURCES = [
  "Formula 1: American Express, Americas payments partner (Oct 2023), global (Oct 2024); Santander, Official Retail Banking Partner (Sep 2024); Standard Chartered, Official Partner (Jan 2026); Crypto.com extended to 2030 (Dec 2024).",
  "Visa press release, 19 Feb 2026 (renewal to 2030, Red Bull Racing car, F1 Academy). McLaren and Mastercard, 28 Aug 2025. Mercedes and Stripe, 20 Oct 2026. McLaren and Airwallex, Oct 2026 extension. Audi and Revolut, 30 Jul 2025. Aston Martin and CoinPayments, 4 Dec 2025 and May 2026.",
  "Ferrari and UniCredit (2025); Ferrari and BingX (from 2026). Williams and Barclays (Feb 2026), BNY (30 Jan 2026), Kraken (renewed Jan 2026). Mercedes and Nu (20 Jan 2026), Nasdaq (Apr 2025). McLaren and FxPro (25 Feb 2026), OKX (to end-2026). Racing Bulls and XMTrading (2026, fourth year). Aston Martin and Coinbase (Feb 2025), Pepperstone (Jun 2025). Alpine and eToro (15 Jan 2026). Red Bull Racing and Gate (2025). Audi and Nexo (16 Jan 2026). Haas and Zoomex (renewed for 2026).",
  "Not counted: Mercado Libre (Alpine; marketplace), Mobilize Financial Services (Renault Group car finance), Gainbridge (no official Cadillac role). Ended before 2026: MoneyGram (Haas title 2023–25), Santander at Ferrari (to 2024) and Williams (to 2025), Bybit at Red Bull Racing (to 2024).",
].join("\n");

async function build() {
  await D.defineLayouts();
  pres.addSection({ title: "Payments landscape" });

  // 1. The map -------------------------------------------------------------
  {
    const s = content("CONTENT", "Payments landscape", TRACK, "Payments landscape",
      t("**27 financial brands** in F1; only **three** handle team payments"),
      SOURCES,
      "The whole map in one view: the series and the 11 teams against five kinds of financial partner. 27 brands in total. The green column is the seat closest to Adyen: a partner inside the team's payments. Only three are live there (Stripe at Mercedes, Airwallex at McLaren, Revolut at Audi); CoinPayments at Aston Martin is exploring digital-asset payments. Card networks buy visibility and access, not the payments operation.");
    const head = (txt, o = {}) => D.hc(txt, { fontSize: 10.5, align: "center", ...o });
    const cell = (txt, ci) => {
      const green = ci === 2;
      const empty = !txt;
      return { text: empty ? "–" : txt, options: { fontSize: 10, align: ci === 0 ? "left" : "center", valign: "middle",
        bold: ci === 0 || (green && !empty), color: empty ? C.accent4 : green ? C.accent2 : C.text1,
        fill: { color: green ? C.accent6 : ci === 0 ? C.background2 : C.background1 } } };
    };
    const rows = [[head("Rights holder", { align: "left" }), head("Card networks"), head("Payments platforms", { fill: { color: C.accent2 } }),
      head("Banks"), head("Trading & investing"), head("Crypto")],
    ...MAP.map((r) => r.map(cell))];
    const rh = MAP.map((r) => (r.some((c) => c.includes("\n")) ? 0.46 : 0.33));
    s.addTable(rows, { x: L, y: 1.62, w: CW, colW: [1.95, 2.25, 2.25, 1.95, 1.8, 1.933], rowH: [0.36, ...rh],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.02, 0.06, 0.02, 0.06], objectName: "Payments map" });
    s.addText([{ text: "Green column: ", options: { bold: true, color: C.accent2 } },
      { text: "a payments or fintech company inside a team's commerce, payouts or finance operations (banks counted separately), the seat closest to Adyen.  *Exploring digital-asset payments.  Announced deals as at 10 Nov 2026.", options: { color: C.text2 } }],
    { x: L, y: 6.52, w: CW, h: 0.3, fontSize: 9.5, margin: 0, isTextBox: true, valign: "middle" });
  }

  // 2. Networks and platforms ----------------------------------------------
  {
    const s = content("CONTENT", "Payments landscape", TRACK, "Payments landscape · Networks and platforms",
      t("Networks buy **visibility and access**; platforms run **payments**"),
      SOURCES,
      "Left: the three card networks. Their deals are about the brand and card-member access (titles, early tickets, experiences). Right: the four platforms that sit inside a team's operations. Two of them, Stripe and Airwallex, are on Adyen's competitor list, and both moved in October 2026: Stripe signed Mercedes on 20 October; Airwallex extended with McLaren and becomes its Official AI Finance Partner from January 2027.");
    const lx = L, lw = 5.7, rx = L + 6.0, rw = R - (L + 6.0), y0 = 1.95;
    label(s, "Card networks", lx, y0, lw);
    label(s, "Payments platforms", rx, y0, rw, C.accent2);
    NETWORKS.forEach(([name, deal, detail], i) => {
      const y = y0 + 0.36 + i * 1.5, h = 1.38;
      card(s, lx, y, lw, h, C.background2);
      s.addText([{ text: name, options: { bold: true, fontSize: 17, color: C.text1, breakLine: true } },
        { text: deal, options: { bold: true, fontSize: 11, color: C.accent2, breakLine: true } },
        { text: detail, options: { fontSize: 10.5, color: C.text2 } }],
      { x: lx + 0.25, y, w: lw - 0.5, h, margin: 0, isTextBox: true, valign: "middle", paraSpaceAfter: 2 });
    });
    PLATFORMS.forEach(([name, deal, peer, detail], i) => {
      const y = y0 + 0.36 + i * 1.125, h = 1.03;
      card(s, rx, y, rw, h, peer ? C.accent6 : C.background2);
      s.addText([{ text: name + "  ", options: { bold: true, fontSize: 15, color: C.text1 } },
        { text: deal, options: { bold: true, fontSize: 10.5, color: C.accent2, breakLine: true } },
        { text: detail, options: { fontSize: 10, color: C.text2 } }],
      { x: rx + 0.25, y, w: rw - 1.6, h, margin: 0, isTextBox: true, valign: "middle", paraSpaceAfter: 2 });
      if (peer) {
        s.addShape(S.ROUNDED_RECTANGLE, { x: R - 1.3, y: y + 0.12, w: 1.1, h: 0.28, rectRadius: 0.06, fill: { color: C.text1 },
          line: { color: C.text1, width: 0 } });
        s.addText("Adyen competitor", { x: R - 1.3, y: y + 0.12, w: 1.1, h: 0.28, fontSize: 8, bold: true, color: C.background1,
          align: "center", valign: "middle", margin: 0, isTextBox: true });
      }
    });
  }

  // 3. Banks, trading and crypto -------------------------------------------
  {
    const s = content("CONTENT", "Payments landscape", TRACK, "Payments landscape · Banks, trading and crypto",
      t("**Banks, trading and crypto** brands sit on 10 of 11 teams"),
      SOURCES,
      "The other 20 financial brands. Banks use F1 for client hospitality and corporate relationships (Barclays and BNY at Williams, Standard Chartered presenting the F1 Business Summit in Las Vegas on 19 Nov 2026). Trading and crypto brands buy reach with fans; crypto is the biggest single group (8 of 27). Only Cadillac has no financial partner. Banks such as Barclays (Williams' main corporate bank) are counted here, not as payments platforms.");
    const cols = [["Banks", BANKS], ["Trading & investing", TRADING], ["Crypto", CRYPTO]];
    const cw = (CW - 0.5) / 3, y0 = 1.95;
    cols.forEach(([head, items], ci) => {
      const x = L + ci * (cw + 0.25);
      label(s, `${head}  (${items.length})`, x, y0, cw, C.accent2);
      card(s, x, y0 + 0.36, cw, 3.72, C.background2);
      const runs = [];
      items.forEach(([name, what], i) => {
        runs.push({ text: name, options: { bold: true, fontSize: 11.5, color: C.text1, breakLine: true, paraSpaceBefore: i ? 5 : 0 } });
        runs.push({ text: what, options: { fontSize: 9.5, color: C.text2, breakLine: i < items.length - 1 } });
      });
      s.addText(runs, { x: x + 0.22, y: y0 + 0.5, w: cw - 0.44, h: 3.5, margin: 0, isTextBox: true, valign: "top" });
    });
    D.soWhat(s, "Most of these deals buy **reach and client hospitality**. A platform inside a team's commerce and payouts is a different seat, and most teams have not filled it.", 6.2);
  }

  // 4. What it means for Adyen ---------------------------------------------
  {
    const s = content("CONTENT", "Payments landscape", TRACK, "Payments landscape · What it means",
      t("Peers are moving, and **7 of 11 teams** have no payments platform"),
      SOURCES,
      "Left: the moves that matter. Stripe signed Mercedes on 20 October 2026 and starts with the team's retail at races this season; Airwallex extended with McLaren the same month. Revolut powers Audi's finance operations and merchandise checkout as title partner. Right: the 11 teams by payments seat. Seven have no payments platform among their announced partners, including Alpine and Ferrari (two of Adyen's routes) and Red Bull Racing (Max's team). Before we pitch, check the category: where a card network is title or team partner (McLaren, Racing Bulls, Red Bull Racing), 'payments' may already be protected.");
    const lx = L, lw = 4.75, y0 = 1.95;
    label(s, "Peers are moving", lx, y0, lw);
    const moves = [
      ["20 Oct 2026", "Stripe × Mercedes", "Official Global Payments Partner. Team retail at races from late 2026; on the car from 2027."],
      ["Oct 2026", "Airwallex × McLaren", "Extension: Official AI Finance Partner from January 2027."],
      ["From 2026", "Revolut × Audi", "Title partner. Powers the team's finance operations and merchandise checkout."],
    ];
    moves.forEach(([when, who, what], i) => {
      const y = y0 + 0.36 + i * 1.32, h = 1.2;
      card(s, lx, y, lw, h, i < 2 ? C.text1 : C.background2);
      const dark = i < 2;
      s.addText([{ text: when, options: { bold: true, fontSize: 10, color: dark ? C.accent1 : C.accent2, breakLine: true } },
        { text: who, options: { bold: true, fontSize: 15, color: dark ? C.background1 : C.text1, breakLine: true } },
        { text: what, options: { fontSize: 10.5, color: dark ? C.accent4 : C.text2 } }],
      { x: lx + 0.25, y, w: lw - 0.5, h, margin: 0, isTextBox: true, valign: "middle" });
    });

    const rx = L + 5.1, rw = R - rx;
    label(s, "Payments seat by team", rx, y0, rw);
    const cols = 4, gap = 0.14, tw = (rw - gap * (cols - 1)) / cols, th = 1.15;
    TEAMS.forEach(([team, partner, route], i) => {
      const x = rx + (i % cols) * (tw + gap), y = y0 + 0.36 + Math.floor(i / cols) * (th + gap);
      const taken = !!partner;
      s.addShape(S.ROUNDED_RECTANGLE, { x, y, w: tw, h: th, rectRadius: 0.08, fill: { color: taken ? C.background2 : C.accent6 },
        line: { color: taken ? C.accent4 : C.accent1, width: taken ? 0.75 : 1.5 } });
      s.addText([{ text: team, options: { bold: true, fontSize: 12.5, color: C.text1, breakLine: true } },
        { text: taken ? partner : "No payments platform", options: { fontSize: 10, bold: !taken, color: taken ? C.text2 : C.accent2 } }],
      { x: x + 0.15, y: y + 0.1, w: tw - 0.3, h: th - 0.45, margin: 0, isTextBox: true, valign: "top" });
      if (route) {
        s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.15, y: y + th - 0.36, w: tw - 0.3, h: 0.24, rectRadius: 0.05, fill: { color: C.text1 },
          line: { color: C.text1, width: 0 } });
        s.addText(`Adyen: ${route}`, { x: x + 0.15, y: y + th - 0.36, w: tw - 0.3, h: 0.24, fontSize: 8.5, bold: true,
          color: C.accent1, align: "center", valign: "middle", margin: 0, isTextBox: true });
      }
    });
    // legend tile
    {
      const i = TEAMS.length, x = rx + (i % cols) * (tw + gap), y = y0 + 0.36 + Math.floor(i / cols) * (th + gap);
      s.addText([{ text: "7 of 11", options: { bold: true, fontSize: 22, color: C.accent2, breakLine: true } },
        { text: "teams with no payments platform", options: { fontSize: 10, color: C.text2 } }],
      { x: x + 0.1, y, w: tw - 0.2, h: th, margin: 0, isTextBox: true, valign: "middle" });
    }
    s.addText([{ text: "Check the category first: ", options: { bold: true, color: C.text1 } },
      { text: "where a card network is a title or team partner (McLaren, Racing Bulls, Red Bull Racing), 'payments' may already be protected.  Payments platform: banks counted separately.  *CoinPayments: exploring digital-asset payments.", options: { color: C.text2 } }],
    { x: L, y: 6.4, w: CW, h: 0.42, fontSize: 10, margin: 0, isTextBox: true, valign: "middle" });
  }

  await pres.writeFile({ fileName: OUT });
  await D.applyTheme(OUT, D.THEME);
  console.log("wrote", OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
