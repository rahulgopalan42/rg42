// F1 partner landscape (October 2026) in the style of the Wolters Kluwer x SPORTFIVE deck.
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const OUT = process.argv[2];
const D = JSON.parse(fs.readFileSync(path.join(__dirname, "data.json"), "utf8"));
const A = (f) => path.join(__dirname, "assets", f);
const byKey = Object.fromEntries(D.teams.map((t) => [t.key, t]));

const THEME = {
  name: "SPORTFIVE",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "000000", lt1: "FFFFFF", dk2: "404040", lt2: "EDEDED",
    accent1: "C00000", accent2: "595959", accent3: "A6A6A6", accent4: "FBE5D7",
    accent5: "848484", accent6: "D9D9D9", hlink: "C00000", folHlink: "7F0000",
  },
};
const HEX = { red: "C00000", dark: "595959", mid: "A6A6A6", ink: "000000", body: "404040", line: "D9D9D9" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5, same as the source deck
pres.theme = { headFontFace: "Calibri", bodyFontFace: "Calibri" };
pres.title = "F1 Partner Landscape 2026";
pres.company = "SPORTFIVE";
const C = pres.SchemeColor;
const S = pres.shapes;
const W = 13.333, L = 0.48, R = 12.85;

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "COVER",
  background: { color: "000000" },
  objects: [
    { image: { x: -0.5, y: -1.0, w: 16.0, h: 9.0, path: A("cover.jpg"), altText: "F1 car, top view" } },
    { image: { x: 0.62, y: 0.55, w: 2.3, h: 0.42, path: path.join(__dirname, "..", "adyen", "build", "assets", "sportfive_white.png"),
        altText: "SPORTFIVE logo" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.62, y: 5.55, w: 9.0, h: 0.75, fontSize: 40, bold: true,
        color: C.background1, margin: 0, valign: "top", align: "left" }, text: "Title" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: 0.62, y: 6.3, w: 9.0, h: 0.4, fontSize: 16, bold: true,
        color: C.background1, charSpacing: 3, margin: 0, valign: "top" }, text: "Subtitle" } },
    { placeholder: { options: { name: "meta", type: "body", x: 0.62, y: 6.75, w: 9.0, h: 0.35, fontSize: 12,
        color: C.accent6, margin: 0, valign: "top" }, text: "Date" } },
  ],
});

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { rect: { x: 0, y: 0, w: W, h: 0.045, fill: { color: C.accent1 } } },
    { image: { x: 10.52, y: 0.27, w: 2.33, h: 0.251, path: A("lockup.png"), altText: "Wolters Kluwer / SPORTFIVE" } },
    { placeholder: { options: { name: "title", type: "title", x: L, y: 0.18, w: 9.8, h: 0.66, fontSize: 36, bold: true,
        color: C.accent1, margin: 0, valign: "middle", align: "left" }, text: "TITLE" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: L, y: 0.88, w: 11.5, h: 0.36, fontSize: 15, bold: true,
        italic: true, color: C.text1, charSpacing: 6, margin: 0, valign: "middle" }, text: "SUBTITLE" } },
    { rect: { x: L, y: 1.38, w: 0.47, h: 0.035, fill: { color: C.accent1 } } },
    { line: { x: L + 0.47, y: 1.397, w: R - L - 0.52, h: 0, line: { color: C.accent6, width: 0.75 } } },
    { rect: { x: R - 0.05, y: 1.375, w: 0.045, h: 0.045, fill: { color: C.accent1 } } },
    { placeholder: { options: { name: "source", type: "body", x: L, y: 7.16, w: 11.3, h: 0.22, fontSize: 7.5,
        color: C.accent5, margin: 0, valign: "middle" }, text: "Source:" } },
  ],
  slideNumber: { x: 12.35, y: 7.12, w: 0.5, h: 0.26, fontSize: 9, color: C.text1, align: "right" },
});

function content(title, subtitle, source, notes) {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText(title.toUpperCase(), { placeholder: "title" });
  s.addText(subtitle.toUpperCase(), { placeholder: "subtitle" });
  s.addText(source, { placeholder: "source" });
  if (notes) s.addNotes(notes);
  return s;
}

// ------------------------------------------------------------------ logos
const LOGO = {
  f1: "f1.png", mercedes: "mercedes.png", redbull: "redbull.png", ferrari: "ferrari.png", mclaren: "mclaren.png",
  alpine: "alpine.png", astonmartin: "astonmartin.png", cadillac: "cadillac.png", audi: "audi.png", haas: "haas.png",
  vcarb: "vcarb.png", williams: "williams.png",
};
const sizeOf = (f) => { // PNG IHDR
  const b = fs.readFileSync(A(f));
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
};
function logo(s, key, x, y, w, h) {
  const { w: pw, h: ph } = sizeOf(LOGO[key]);
  const k = Math.min(w / pw, h / ph);
  const lw = pw * k, lh = ph * k;
  s.addImage({ path: A(LOGO[key]), x: x + (w - lw) / 2, y: y + (h - lh) / 2, w: lw, h: lh, altText: byKey[key].name + " logo" });
}

// ------------------------------------------------------------------ ecosystem matrix (slide 15/16 format)
const ROW_LABELS = ["TITLE /\nPRINCIPAL\nPARTNER", "OFFICIAL /\nTEAM\nPARTNER", "SUPPLIER /\nREGIONAL /\nLICENSEE"];
const ROW_FILL = [C.accent4, C.background1, C.background2];
const SEP = "\u00A0\u00A0·  ";
const keepWhole = (t) => t.replace(/ /g, "\u00A0").replace(/-/g, "\u2011");

function cellRuns(partners, fontSize) {
  const runs = [];
  partners.forEach((p, i) => {
    const focus = p.sector !== "O";
    runs.push({ text: keepWhole(p.name), options: { bold: focus, color: p.new ? HEX.red : focus ? HEX.ink : HEX.body, fontSize } });
    if (i < partners.length - 1) runs.push({ text: SEP, options: { color: HEX.mid, fontSize } });
  });
  return runs;
}
// rough line count for a run of names in a column of width w (inches), Calibri
function linesNeeded(partners, w, fontSize) {
  const per = (fontSize / 72) * 0.5; // average Calibri glyph width incl. bold slack
  const cap = w / per;
  let lines = 1, cur = 0;
  partners.forEach((p, i) => {
    const len = p.name.length + (i < partners.length - 1 ? SEP.length : 0);
    if (cur + len > cap && cur > 0) { lines++; cur = len; } else cur += len;
  });
  return partners.length ? lines : 0;
}

function ecosystem(groups, part, total) {
  const s = content("Partner ecosystem", `Current team partners, all sectors (${part}/${total})`,
    "Source: official team partner pages (read 29 Oct 2026); f1salaries.com (30 Sep 2026) for Ferrari, McLaren and Cadillac; RTR Sports (6 Oct 2026) for F1. Tiers harmonised by SPORTFIVE; see Notes & Sources.",
    "Every current partner by tier. Bold = Wolters Kluwer focus sectors (financial services, professional services, life sciences & health). Red = partnership announced in 2026.");
  const labelW = 1.02, gx0 = L + labelW + 0.1, gap = 0.22;
  const cols = groups.reduce((n, g) => n + g.keys.length, 0);
  const usable = R - gx0 - gap * (groups.length - 1);
  const colW = usable / cols;
  const headY = 1.88, headH = 0.82, top = headY + headH, bottom = 6.72, pad = 0.07;
  // choose the largest font that fits all three tier rows
  let fontSize, rowH;
  for (fontSize of [11, 10.5, 10, 9.5, 9, 8.5, 8, 7.5]) {
    const lh = (fontSize / 72) * 1.22;
    rowH = [1, 2, 3].map((r) => Math.max(...groups.flatMap((g) => g.keys.map((k) =>
      linesNeeded(byKey[k].partners.filter((p) => p.row === r), colW - 2 * pad - 0.04, fontSize) * lh))) + 2 * pad);
    rowH = rowH.map((h) => Math.max(h, 0.5));
    if (rowH.reduce((a, b) => a + b, 0) <= bottom - top) break;
  }
  const spare = bottom - top - rowH.reduce((a, b) => a + b, 0);
  rowH = rowH.map((h) => h + Math.max(spare, 0) * (h / rowH.reduce((a, b) => a + b, 0)));
  const rowY = [top, top + rowH[0], top + rowH[0] + rowH[1]];
  // tier labels
  ROW_LABELS.forEach((lab, i) => s.addText(lab, { x: L, y: rowY[i], w: labelW, h: rowH[i], fontSize: 8.5, bold: true,
    align: "right", valign: "middle", color: C.text1, margin: 0, isTextBox: true }));
  let x = gx0;
  for (const g of groups) {
    const gw = colW * g.keys.length;
    s.addText(g.label, { x: x + 0.05, y: headY - 0.32, w: gw, h: 0.28, fontSize: 12, bold: true, color: C.text1, margin: 0, isTextBox: true });
    // tier bands
    rowY.forEach((y, i) => s.addShape(S.RECTANGLE, { x: x + 0.06, y, w: gw - 0.12, h: rowH[i], fill: { color: ROW_FILL[i] },
      line: { color: ROW_FILL[i], width: 0 } }));
    s.addShape(S.LINE, { x: x + 0.06, y: top, w: gw - 0.12, h: 0, line: { color: C.accent6, width: 1 } });
    g.keys.forEach((k, j) => {
      const cx = x + j * colW, t = byKey[k];
      if (j) s.addShape(S.LINE, { x: cx, y: headY + 0.06, w: 0, h: bottom - headY - 0.12, line: { color: C.accent6, width: 0.75 } });
      logo(s, k, cx + 0.15, headY + 0.07, colW - 0.3, 0.5);
      const isNewTeam = k === "audi" || k === "cadillac";
      s.addText([{ text: `${t.partners.length} PARTNERS`, options: { bold: true, color: HEX.red } },
        ...(isNewTeam ? [{ text: "  ·  NEW TEAM 2026", options: { bold: true, color: HEX.dark } }] : [])],
      { x: cx, y: headY + 0.58, w: colW, h: 0.2, fontSize: 8, align: "center", charSpacing: 1, margin: 0, isTextBox: true });
      [1, 2, 3].forEach((r, i) => {
        const ps = t.partners.filter((p) => p.row === r);
        if (!ps.length) return;
        s.addText(cellRuns(ps, fontSize), { x: cx + pad, y: rowY[i] + pad * 0.6, w: colW - 2 * pad, h: rowH[i] - pad * 1.2,
          valign: "middle", align: "center", margin: 0, lineSpacingMultiple: 1.0, isTextBox: true, fit: "none" });
      });
    });
    s.addShape(S.ROUNDED_RECTANGLE, { x: x - 0.02, y: headY - 0.02, w: gw + 0.04, h: bottom - headY + 0.06, rectRadius: 0.12,
      fill: { type: "none" }, line: { color: g.central ? "F08080" : C.accent5, width: 2 } });
    x += gw + gap;
  }
  // legend
  s.addText([
    { text: "Bold", options: { bold: true, color: HEX.ink } },
    { text: " = Wolters Kluwer focus sectors (financial services, professional services, life sciences & health)      ", options: { color: HEX.body } },
    { text: "Red", options: { bold: true, color: HEX.red } },
    { text: " = partnership announced in 2026", options: { color: HEX.body } },
  ], { x: L, y: 6.86, w: 11.0, h: 0.24, fontSize: 9, margin: 0, isTextBox: true, valign: "middle" });
  return s;
}

// ------------------------------------------------------------------ slides
const teams = D.teams.filter((t) => t.key !== "f1");
const n = (t) => t.partners.length;
const focus = (t, sec) => t.partners.filter((p) => (sec ? p.sector === sec : p.sector !== "O")).length;
const totalTeam = teams.reduce((a, t) => a + n(t), 0);
const brandCounts = {};
teams.forEach((t) => t.partners.forEach((p) => (brandCounts[p.name] = (brandCounts[p.name] || 0) + 1)));
const uniqueBrands = Object.keys(brandCounts).length;
const multiBrands = Object.values(brandCounts).filter((v) => v > 1).length;
const SHORT = { mercedes: "Mercedes", redbull: "Red Bull Racing", ferrari: "Ferrari", mclaren: "McLaren", alpine: "Alpine",
  astonmartin: "Aston Martin", cadillac: "Cadillac", audi: "Audi", haas: "Haas", vcarb: "Racing Bulls", williams: "Williams", f1: "F1 (central)" };

async function build() {
  // 1 Cover
  {
    const s = pres.addSlide({ masterName: "COVER" });
    s.addText("F1 PARTNER LANDSCAPE", { placeholder: "title" });
    s.addText("CURRENT PARTNER ECOSYSTEM BY TEAM", { placeholder: "subtitle" });
    s.addText("Prepared for Wolters Kluwer  ·  October 2026", { placeholder: "meta" });
  }

  // 2 Partners per team
  {
    const s = content("Partner landscape", "Which teams have the most partners",
      "Source: official team partner pages (read 29 Oct 2026); f1salaries.com (30 Sep 2026); RTR Sports (6 Oct 2026). Counts include title, official and supplier partners as listed by each team.",
      `Team partnerships: ${totalTeam} across 11 teams; ${uniqueBrands} distinct brands; ${multiBrands} brands partner more than one team (Pirelli supplies all 11).`);
    const sorted = [...teams].sort((a, b) => n(b) - n(a));
    s.addText("NUMBER OF PARTNERS PER TEAM (2026)", { x: L, y: 1.62, w: 8, h: 0.3, fontSize: 12, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addChart(pres.charts.BAR, [{ name: "Partners", labels: sorted.map((t) => SHORT[t.key]), values: sorted.map(n) }], {
      x: L - 0.1, y: 1.95, w: 8.3, h: 4.95, barDir: "bar", catAxisOrientation: "maxMin", barGapWidthPct: 45,
      chartColors: sorted.map((t, i) => (i < 3 ? HEX.red : HEX.dark)),
      catAxisLabelColor: HEX.ink, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt", catAxisLineShow: false,
      valAxisHidden: true, valGridLine: { style: "none" }, valAxisMinVal: 0, valAxisMaxVal: 60,
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: HEX.ink, dataLabelFontSize: 12, dataLabelFontBold: true,
      dataLabelFontFace: "+mn-lt", showLegend: false,
    });
    const tiles = [
      [String(totalTeam), "team partnerships across the 11 teams"],
      [String(Math.round(totalTeam / teams.length)), "partners per team on average"],
      [String(byKey.f1.partners.length), "partners at F1 level (central organisation)"],
      [String(uniqueBrands), `distinct brands; ${multiBrands} partner more than one team`],
    ];
    tiles.forEach(([big, lab], i) => {
      const y = 1.95 + i * 1.22, x = 9.1, w = R - 9.1;
      s.addShape(S.RECTANGLE, { x, y, w, h: 1.08, fill: { color: C.background2 }, line: { color: C.background2, width: 0 } });
      s.addText(big, { x: x + 0.25, y: y + 0.08, w: 1.55, h: 0.9, fontSize: 34, bold: true, color: C.accent1, margin: 0,
        valign: "middle", isTextBox: true });
      s.addText(lab, { x: x + 1.8, y: y + 0.08, w: w - 2.0, h: 0.9, fontSize: 12, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
    });
    s.addText([{ text: "McLaren (52), Alpine (48) and Ferrari (41) ", options: { bold: true } },
      { text: "run the largest portfolios. New entrant Cadillac has the fewest (11)." }],
    { x: L, y: 6.82, w: 12, h: 0.3, fontSize: 11, color: C.text1, margin: 0, isTextBox: true });
  }

  // 3 Focus sectors
  {
    const s = content("Relevant partner mapping", "Team partners in Wolters Kluwer focus sectors",
      "Source: as previous slide. Sector classification by SPORTFIVE: financial services = banking, payments, trading, crypto, insurance, asset management; professional services = consulting, legal, HR and learning; life sciences & health = pharma, healthcare providers, health services.",
      "Share of each team's partners in the three focus sectors. F1 shown for reference.");
    const all = [...D.teams].sort((a, b) => focus(b) - focus(a) || n(b) - n(a));
    const lab = all.map((t) => `${SHORT[t.key]}\n${Math.round((100 * focus(t)) / n(t))}%`);
    s.addText("NUMBER OF FOCUS-SECTOR PARTNERS (AND SHARE OF ALL PARTNERS)", { x: L, y: 1.62, w: 9, h: 0.3, fontSize: 12, bold: true,
      color: C.text1, margin: 0, isTextBox: true });
    s.addChart(pres.charts.BAR, [
      { name: "Financial services", labels: lab, values: all.map((t) => focus(t, "FS")) },
      { name: "Professional services", labels: lab, values: all.map((t) => focus(t, "PS")) },
      { name: "Life sciences & health", labels: lab, values: all.map((t) => focus(t, "LS")) },
    ], {
      x: L - 0.1, y: 1.95, w: 8.9, h: 4.85, barDir: "col", barGrouping: "stacked", barGapWidthPct: 45,
      chartColors: [HEX.red, HEX.dark, HEX.mid],
      catAxisLabelColor: HEX.ink, catAxisLabelFontSize: 10, catAxisLabelFontFace: "+mn-lt", catAxisLineShow: false,
      valAxisHidden: true, valGridLine: { style: "none" }, valAxisMinVal: 0,
      showValue: true, dataLabelPosition: "ctr", dataLabelColor: "FFFFFF", dataLabelFontSize: 10, dataLabelFontBold: true, dataLabelFormatCode: "0;-0;;@",
      dataLabelFontFace: "+mn-lt", showLegend: true, legendPos: "t", legendFontSize: 10, legendFontFace: "+mn-lt", legendColor: HEX.ink,
    });
    const fsN = teams.reduce((a, t) => a + focus(t, "FS"), 0), psN = teams.reduce((a, t) => a + focus(t, "PS"), 0),
      lsN = teams.reduce((a, t) => a + focus(t, "LS"), 0);
    const tiles = [
      [String(fsN), "financial services", "Banks, payments, trading and crypto: the largest focus sector on the grid (e.g. Mastercard, UBS, Barclays, Goldman Sachs)."],
      [String(psN), "professional services", "Consulting, legal, HR and learning (e.g. Deloitte, Ashurst, Morrison Foerster, Randstad, Workday)."],
      [String(lsN), "life sciences & health", "AbbVie (McLaren, new Oct 2026), UChicago Medicine (Haas), JAAQ (Alpine)."],
    ];
    tiles.forEach(([big, head, body], i) => {
      const y = 1.95 + i * 1.62, x = 9.45, w = R - 9.45;
      s.addShape(S.RECTANGLE, { x, y, w, h: 1.48, fill: { color: C.background2 }, line: { color: C.background2, width: 0 } });
      s.addText([{ text: big + "  ", options: { fontSize: 30, bold: true, color: HEX.red } },
        { text: head.toUpperCase(), options: { fontSize: 11, bold: true, color: HEX.ink } }],
      { x: x + 0.22, y: y + 0.08, w: w - 0.44, h: 0.55, margin: 0, valign: "middle", isTextBox: true });
      s.addText(body, { x: x + 0.22, y: y + 0.63, w: w - 0.44, h: 0.78, fontSize: 10.5, color: C.text1, margin: 0, valign: "top", isTextBox: true });
    });
  }

  // 4 What changed in 2026
  {
    const s = content("What's changed", "The 2026 partner landscape at a glance",
      "Source: team and partner announcements; Sportcal, Insider Sport and The Race (Oct 2026); GPblog and GrandPrix.com (Dec 2025 to Feb 2026); f1salaries.com; RTR Sports.",
      "Title changes, the main new deals announced in 2026, exits, and deals already signed for 2027. New-deal count: 28 partnerships announced in 2026 (to 29 Oct) across the grid and F1; technology & AI 9 (Microsoft, Rubrik, IFS, TWG AI, Core Scientific, ElevenLabs, Aleph, Adobe, RUCKUS), financial services 7 (Hedera, Stripe, Nexo, Libertex, eToro, Standard Chartered, Marsh).");
    const cols = [
      ["GRID & TITLE CHANGES", [
        ["Two new teams: ", "Audi (formerly Sauber; Revolut title partner) and Cadillac, the 11th team (no title partner)."],
        ["New naming partners: ", "Mastercard at McLaren; Toyota Gazoo Racing at Haas (replacing MoneyGram)."],
        ["Renewed: ", "Oracle with Red Bull Racing (Feb); Visa across both Red Bull teams through 2030 (Feb)."],
        ["Power units: ", "Honda moves from Red Bull to Aston Martin as works partner."],
      ]],
      ["NEW DEALS ANNOUNCED IN 2026", [
        ["McLaren: ", "PUMA, Schneider Electric, Hedera, Rubrik (Jan); Etihad (Feb); Global (May); SharkNinja (Sep); AbbVie (Oct)."],
        ["Mercedes: ", "Microsoft (Jan); Stripe (Oct, from 2027)."],
        ["Cadillac: ", "IFS, Tenneco, Claro (Jan); TWG AI (Feb); Core Scientific (Mar); 3M (Jun); Frontieras (Oct)."],
        ["Audi: ", "Nexo, ElevenLabs, Aleph (Jan); Libertex (Mar)."],
        ["Others: ", "DAMAC (Red Bull, Feb); eToro and Adobe (Alpine, Jan and Oct); Castore and RUCKUS (Haas, Jan); Standard Chartered and Marsh (F1, Jan and Apr)."],
      ]],
      ["EXITS & 2027 PIPELINE", [
        ["Exits: ", "Santander left Williams (Feb; still an F1 official partner); MoneyGram left Haas; Kick and Stake left with Sauber's rebrand to Audi; Castore replaced by PUMA at McLaren."],
        ["Signed for 2027: ", "Stripe becomes Mercedes' global payments partner; Rakuten joins Ferrari from 1 Jan 2027; Adobe's Alpine activations start with the 2027 season."],
        ["Up for renewal: ", "OKX's McLaren deal runs to the end of 2026."],
      ]],
    ];
    const newDeals = D.teams.reduce((a, t) => a + t.partners.filter((p) => p.new).length, 0);
    s.addShape(S.RECTANGLE, { x: L, y: 6.42, w: R - L, h: 0.58, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
    s.addText([{ text: `${newDeals} new partnerships announced in 2026: `, options: { bold: true } },
      { text: "technology & AI (9) and financial services (7) account for more than half." }],
    { x: L + 0.25, y: 6.42, w: R - L - 0.5, h: 0.58, fontSize: 14, color: C.background1, margin: 0, valign: "middle", isTextBox: true });
    const cw = (R - L - 0.6) / 3;
    cols.forEach(([head, items], i) => {
      const x = L + i * (cw + 0.3), y = 1.7, h = 4.55;
      s.addShape(S.RECTANGLE, { x, y, w: cw, h, fill: { color: i === 1 ? C.accent4 : C.background2 }, line: { color: C.background2, width: 0 } });
      s.addText(head, { x: x + 0.25, y: y + 0.2, w: cw - 0.5, h: 0.32, fontSize: 13, bold: true, color: C.accent1, charSpacing: 1,
        margin: 0, isTextBox: true });
      s.addText(items.map(([b, t], k) => [{ text: b, options: { bold: true, color: HEX.ink, bullet: { code: "25A0" } } },
        { text: t, options: { color: HEX.ink, breakLine: k < items.length - 1 } }]).flat(),
      { x: x + 0.25, y: y + 0.65, w: cw - 0.5, h: h - 0.8, fontSize: 12.5, margin: 0, valign: "top", paraSpaceAfter: 9, isTextBox: true });
    });
  }

  // 5-8 Ecosystem
  const parts = [
    [{ label: "Central Organisation", keys: ["f1"], central: true }, { label: "Podium Teams", keys: ["mercedes", "redbull"] }],
    [{ label: "Podium Teams", keys: ["ferrari", "mclaren"] }],
    [{ label: "Challenger Teams", keys: ["alpine", "astonmartin", "cadillac"] }],
    [{ label: "Challenger Teams", keys: ["audi", "haas", "vcarb", "williams"] }],
  ];
  parts.forEach((g, i) => ecosystem(g, i + 1, parts.length));

  // 9 Notes & sources
  {
    const s = content("Notes & sources", "How this landscape was built", "Prepared by SPORTFIVE for Wolters Kluwer, October 2026.",
      "Method and per-team sources, for any question on a count or a tier.");
    const notes = [
      ["Scope", "All commercial partners listed for the 2026 season by the 11 teams and Formula 1, including suppliers and licensees. Counts are partners as each team lists them; sub-brands of one deal are counted once where the source does so (e.g. Google at McLaren)."],
      ["Tiers", "Harmonised to three rows. Title / principal = naming, title, principal, premium and primary partners. Supplier / regional / licensee = partners the team labels as such. Red Bull, Williams, Haas and Racing Bulls do not label tiers: their title partners (and Visa at Red Bull, Barclays and Komatsu at Williams) are shown as principal, tyre and safety-equipment suppliers as suppliers, and all others as official / team partners."],
      ["New in 2026", "Partnership publicly announced in calendar 2026 (to 29 Oct). Renewals and extensions are not marked."],
      ["Caveats", "Ferrari's, McLaren's and Cadillac's own partner pages could not be read, so these use f1salaries.com (30 Sep 2026), plus AbbVie (McLaren) and Frontieras (Cadillac), both announced in October. Gainbridge and UKG, shown for Cadillac in the September deck, are not on current lists."],
    ];
    notes.forEach(([h, b], i) => {
      const y = 1.7 + i * 1.22;
      s.addText(h.toUpperCase(), { x: L, y, w: 1.6, h: 1.1, fontSize: 12, bold: true, color: C.accent1, margin: 0, valign: "top", isTextBox: true });
      s.addText(b, { x: L + 1.7, y, w: 5.9, h: 1.15, fontSize: 11, color: C.text1, margin: 0, valign: "top", isTextBox: true });
    });
    s.addText("SOURCES BY TEAM", { x: 8.3, y: 1.7, w: 4.5, h: 0.3, fontSize: 11, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText(D.teams.map((t, i) => [{ text: SHORT[t.key] + ": ", options: { bold: true } },
      { text: D.sources[t.key], options: { breakLine: i < D.teams.length - 1 } }]).flat(),
    { x: 8.3, y: 2.05, w: R - 8.3, h: 4.9, fontSize: 9.5, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 3, isTextBox: true });
  }

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
}
build().catch((e) => { console.error(e); process.exit(1); });
