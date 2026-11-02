// Adyen x Formula 1: board-prep deck template.
// Why-F1 and competitive slides are built from the SPORTFIVE BI data; opportunity,
// recommendation, rights and investment slides are structured placeholders.
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const Fi = require("react-icons/fi");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const OUT = process.argv[2] || "Adyen_x_F1.pptx";
const A = (f) => path.join(__dirname, "assets", f);

// ------------------------------------------------------------------ brand
const THEME = {
  name: "Adyen",
  headFontFace: "Inter",
  bodyFontFace: "Inter",
  colors: {
    dk1: "00112C", // Adyen navy
    lt1: "FFFFFF",
    dk2: "404B5F", // slate body text
    lt2: "F7F8F9", // card grey
    accent1: "0ABF53", // Adyen green
    accent2: "079A44", // deep green
    accent3: "8F97A3", // muted grey
    accent4: "D5DAE0", // hairline
    accent5: "1B2A44", // navy, raised
    accent6: "E6F8ED", // green tint
    hlink: "079A44",
    folHlink: "079A44",
  },
};
// chart options that only take hex
const HEX = { navy: "00112C", green: "0ABF53", slate: "404B5F", muted: "8F97A3", context: "C9CFD6", hair: "E3E6EA" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Adyen x Formula 1";
pres.company = "SPORTFIVE";
const C = pres.SchemeColor;
const S = pres.shapes;

const W = 13.333, L = 0.6, R = 12.733, CW = R - L;

// ------------------------------------------------------------------ icons
const iconCache = {};
async function icon(name, color) {
  const key = name + color;
  if (!iconCache[key]) {
    const svg = ReactDOMServer.renderToStaticMarkup(
      React.createElement(Fi[name], { color: "#" + color, size: 256, strokeWidth: 1.8 })
    );
    const buf = await sharp(Buffer.from(svg)).png().toBuffer();
    iconCache[key] = "image/png;base64," + buf.toString("base64");
  }
  return iconCache[key];
}

// ------------------------------------------------------------------ layouts
let PHOTO_ICON_DARK, PHOTO_ICON_LIGHT;
async function defineLayouts() {
PHOTO_ICON_DARK = await icon("FiImage", "8F97A3");
PHOTO_ICON_LIGHT = await icon("FiImage", "8F97A3");
const footerObjects = (logo) => [
  { image: { x: 11.42, y: 6.98, w: 0.68, h: 0.22, path: A(logo), altText: "Adyen logo" } },
];

pres.defineSlideMaster({
  title: "COVER",
  background: { color: C.text1 },
  objects: [
    { rect: { x: 7.0, y: 0, w: W - 7.0, h: 7.5, fill: { color: C.accent5 } } },
    { image: { x: 7.0 + (W - 7.0) / 2 - 0.3, y: 3.2, w: 0.6, h: 0.6, data: PHOTO_ICON_DARK } },
    { text: { text: "Cover photo", options: { x: 7.0, y: 3.9, w: W - 7.0, h: 0.35, fontSize: 12, color: C.accent3, align: "center" } } },
    { placeholder: { options: { name: "photo", type: "image", x: 7.0, y: 0, w: W - 7.0, h: 7.5, color: C.background1 },
        text: "Add cover photo (car, race or Adyen at the track)" } },
    { placeholder: { options: { name: "eyebrow", type: "body", x: L, y: 1.75, w: 5.9, h: 0.35, fontSize: 12, bold: true,
        color: C.accent1, charSpacing: 2, margin: 0, valign: "top" }, text: "EYEBROW" } },
    { placeholder: { options: { name: "title", type: "title", x: L, y: 2.15, w: 6.2, h: 2.1, fontSize: 54, color: C.background1,
        margin: 0, valign: "top", align: "left" }, text: "Title" } },
    { placeholder: { options: { name: "subtitle", type: "body", x: L, y: 4.35, w: 5.9, h: 0.9, fontSize: 18,
        color: C.accent4, margin: 0, valign: "top" }, text: "Subtitle" } },
    { placeholder: { options: { name: "meta", type: "body", x: L, y: 5.45, w: 5.9, h: 0.35, fontSize: 12,
        color: C.accent3, margin: 0, valign: "top" }, text: "Prepared for · date" } },
    { image: { x: L, y: 6.55, w: 1.12, h: 0.36, path: A("adyen_green.png"), altText: "Adyen logo" } },
    { line: { x: 1.98, y: 6.55, w: 0, h: 0.36, line: { color: C.accent3, width: 0.75 } } },
    { image: { x: 2.2, y: 6.62, w: 1.2, h: 0.22, path: A("sportfive_white.png"), altText: "SPORTFIVE logo" } },
  ],
});

pres.defineSlideMaster({
  title: "DIVIDER",
  background: { color: C.text1 },
  objects: [
    { placeholder: { options: { name: "num", type: "body", x: L, y: 1.6, w: 4, h: 1.3, fontSize: 80, bold: true,
        color: C.accent1, margin: 0, valign: "top" }, text: "01" } },
    { placeholder: { options: { name: "title", type: "title", x: L, y: 3.05, w: 10, h: 1.0, fontSize: 44, color: C.background1,
        margin: 0, valign: "top", align: "left" }, text: "Section title" } },
    { placeholder: { options: { name: "desc", type: "body", x: L, y: 4.15, w: 8.5, h: 0.9, fontSize: 18, color: C.accent4,
        margin: 0, valign: "top" }, text: "What this section answers" } },
    { image: { x: R - 1.12, y: 0.55, w: 1.12, h: 0.36, path: A("adyen_green.png"), altText: "Adyen logo" } },
  ],
});

const contentObjects = (x, w) => [
  { placeholder: { options: { name: "eyebrow", type: "body", x, y: 0.42, w, h: 0.3, fontSize: 11, bold: true, color: C.accent1,
      charSpacing: 1.5, margin: 0, valign: "top" }, text: "SECTION · TOPIC" } },
  { placeholder: { options: { name: "title", type: "title", x, y: 0.75, w, h: 1.0, fontSize: 28, color: C.text1,
      margin: 0, valign: "top", align: "left" }, text: "Action title: the one thing this slide proves" } },
  { placeholder: { options: { name: "source", type: "body", x, y: 6.98, w: 10.6 - x, h: 0.24, fontSize: 9, color: C.accent3,
      margin: 0, valign: "middle" }, text: "Source:" } },
  ...footerObjects("adyen_green.png"),
];
const slideNumber = { x: 12.18, y: 6.98, w: 0.55, h: 0.22, fontSize: 9, color: C.accent3, align: "right" };

pres.defineSlideMaster({ title: "CONTENT", background: { color: C.background1 }, objects: contentObjects(L, CW), slideNumber });

pres.defineSlideMaster({
  title: "CONTENT_PHOTO",
  background: { color: C.background1 },
  objects: [
    { rect: { x: 0, y: 0, w: 4.85, h: 7.5, fill: { color: C.background2 } } },
    { image: { x: 4.85 / 2 - 0.3, y: 3.2, w: 0.6, h: 0.6, data: PHOTO_ICON_LIGHT } },
    { text: { text: "Photo of the asset", options: { x: 0, y: 3.9, w: 4.85, h: 0.35, fontSize: 12, color: C.accent3, align: "center" } } },
    { placeholder: { options: { name: "photo", type: "image", x: 0, y: 0, w: 4.85, h: 7.5, color: C.text2 },
        text: "Add photo of the asset" } },
    ...contentObjects(5.35, R - 5.35),
  ],
  slideNumber,
});

}

// ------------------------------------------------------------------ helpers
const SECTIONS = ["Why Formula 1", "Competitive landscape", "The opportunities", "Recommendation"];

function content(master, section, eyebrow, title, source, notes) {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  s.addText(eyebrow.toUpperCase(), { placeholder: "eyebrow" });
  s.addText(title, { placeholder: "title" });
  s.addText(source, { placeholder: "source" });
  if (notes) s.addNotes(notes);
  return s;
}

// title runs: plain text with **highlight** in Adyen green
function t(str) {
  return str.split(/(\*\*[^*]+\*\*)/).filter(Boolean).map((part) =>
    part.startsWith("**") ? { text: part.slice(2, -2), options: { color: C.accent1 } } : { text: part });
}

function card(s, x, y, w, h, fill = C.background2, name = "Card") {
  s.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: fill, width: 0 },
    objectName: name });
}

// a dashed box the team fills in; label is the instruction
function ph(s, x, y, w, h, label, { dark = false, size = 12, align = "center" } = {}) {
  s.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: dark ? C.accent5 : C.background1 },
    line: { color: C.accent3, width: 1, dashType: "dash" }, objectName: "Placeholder" });
  s.addText([{ text: "[ADD] ", options: { bold: true, color: dark ? C.accent1 : C.accent2 } },
    { text: label, options: { italic: true, color: dark ? C.accent4 : C.text2 } }],
  { x: x + 0.12, y, w: w - 0.24, h, fontSize: size, align, valign: "middle", margin: 0, isTextBox: true, objectName: "Placeholder text" });
}

// inline placeholder runs for use inside text
const add = (label, size) => [
  { text: "[ADD] ", options: { bold: true, color: C.accent2, fontSize: size } },
  { text: label, options: { italic: true, color: C.text2, fontSize: size } },
];

function label(s, text, x, y, w, color = C.text2) {
  s.addText(text.toUpperCase(), { x, y, w, h: 0.26, fontSize: 10.5, bold: true, color, charSpacing: 1.2, margin: 0,
    isTextBox: true, valign: "top" });
}

function soWhat(s, text, y = 6.15) {
  card(s, L, y, CW, 0.58, C.accent6, "So what");
  s.addText([{ text: "So what  ", options: { bold: true, color: C.accent2 } }, ...t(text).map((r) => ({
    text: r.text, options: { color: C.text1, bold: !!r.options } }))],
  { x: L + 0.25, y, w: CW - 0.5, h: 0.58, fontSize: 13, valign: "middle", margin: 0, isTextBox: true });
}

async function iconDot(s, name, x, y, d = 0.5, bg = C.accent1, fg = "FFFFFF") {
  s.addShape(S.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { color: bg, width: 0 } });
  const p = d * 0.24;
  s.addImage({ data: await icon(name, fg), x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p });
}

function divider(n, title, desc, notes) {
  const s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: SECTIONS[n - 1] });
  s.addText(String(n).padStart(2, "0"), { placeholder: "num" });
  s.addText(title, { placeholder: "title" });
  s.addText(desc, { placeholder: "desc" });
  const tw = CW / 4;
  SECTIONS.forEach((name, i) => {
    const on = i === n - 1;
    s.addShape(S.LINE, { x: L + i * tw, y: 6.25, w: tw - 0.2, h: 0, line: { color: on ? C.accent1 : C.accent5, width: 2 } });
    s.addText([{ text: String(i + 1).padStart(2, "0") + "  ", options: { bold: true, color: on ? C.accent1 : C.accent3 } },
      { text: name, options: { color: on ? C.background1 : C.accent3, bold: on } }],
    { x: L + i * tw, y: 6.35, w: tw - 0.2, h: 0.4, fontSize: 12, margin: 0, isTextBox: true, valign: "top" });
  });
  if (notes) s.addNotes(notes);
  return s;
}

const chartBase = () => ({
  catAxisLabelColor: HEX.slate, catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt",
  catAxisLineShow: false, catGridLine: { style: "none" },
  valAxisHidden: true, valGridLine: { style: "none" }, valAxisLineShow: false,
  showValue: true, dataLabelColor: HEX.navy, dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt", dataLabelFontBold: true,
  dataLabelPosition: "outEnd", showLegend: false, barGapWidthPct: 55,
});

// ------------------------------------------------------------------ data (SPORTFIVE BI)
const AUDIENCE = { years: ["2022", "2023", "2024", "2025", "2026"], values: [478.0, 495.1, 546.6, 577.5, 625.3] };
const DEALS = { years: ["2020", "2021", "2022", "2023", "2024", "2025"], values: [0.893, 1.007, 1.751, 1.200, 0.982, 2.368] };
const AFFINITY = [
  ["Formula 1", 132.4, 146.9, 166.6, 142.8, 237.9],
  ["Tennis", 129.5, 128.4, 148.1, 141.8, 176.3],
  ["Cycling", 113.1, 124.7, 139.1, 120.4, 181.8],
  ["Basketball", 117.9, 117.4, 131.1, 120.3, 151.1],
  ["Football", 108.5, 117.0, 121.2, 111.9, 131.2],
];
const MARKETS = [ // top 11 of 22 Adyen office markets by F1 audience (M), growth 2022-26, 2027 race
  ["China", 122.6, "+20.9%", true], ["India", 117.4, "+94.9%", false], ["Brazil", 49.8, "−2.2%", true],
  ["United States", 40.8, "+74.3%", true], ["Mexico", 21.8, "−2.2%", true], ["United Kingdom", 14.8, "+48.2%", true],
  ["Germany", 13.7, "+19.8%", false], ["Italy", 13.6, "+11.8%", true], ["Spain", 12.0, "+18.9%", true],
  ["France", 9.2, "+30.8%", false], ["Japan", 7.1, "+41.2%", true],
];
const REGIONS = [ // offices, races, office cities that host a race
  ["Europe", ["Amsterdam", "Berlin", "Brussels", "London", "Manchester", "Madrid", "Milan", "Munich", "Paris", "Prague", "Stockholm", "Warsaw"],
    ["Portimão", "Silverstone", "Monaco", "Spa-Francorchamps", "Spielberg", "Budapest", "Monza", "Madrid", "Baku", "Istanbul"], "Madrid"],
  ["North America", ["San Francisco", "Chicago", "New York", "Toronto", "Mexico City"], ["Las Vegas", "Austin", "Miami", "Montreal", "Mexico City"], "Mexico City"],
  ["East Asia", ["Shanghai", "Hong Kong", "Tokyo"], ["Shanghai", "Suzuka"], "Shanghai"],
  ["Southeast Asia", ["Kuala Lumpur", "Singapore"], ["Singapore"], "Singapore"],
  ["South America", ["São José dos Campos", "São Paulo"], ["São Paulo"], "São Paulo"],
  ["India", ["Mumbai", "Bengaluru"], [], "No race"],
  ["Middle East", ["Dubai"], ["Sakhir", "Jeddah", "Lusail", "Abu Dhabi"], "—"],
  ["Australia", ["Sydney"], ["Melbourne"], "—"],
];
const COMPETITORS = [ // name, F1, football, US leagues & college, other sport & venues
  ["Stripe", "Mercedes-AMG Petronas F1 Team", "", "", "Ryder Cup"],
  ["Airwallex", "McLaren F1 Team", "Arsenal FC", "San Francisco Giants", "Essendon FC"],
  ["PayPal", "", "Liverpool FC, San Jose Earthquakes", "Seattle Seahawks, NFL, Big 12 Conference", ""],
  ["Fiserv", "", "", "", "Clover Park, Fiserv Forum"],
  ["Shift4", "", "Austin FC, Charlotte FC, Chicago Fire FC, LAFC, San Diego FC, Sporting KC",
    "Kansas City Chiefs, Las Vegas Raiders, New Orleans Saints, Chicago Cubs, Texas Rangers", ""],
  ["Global Payments", "", "", "Minnesota Twins, Philadelphia 76ers", "Mercedes-Benz Stadium"],
  ["Ant International", "", "Argentinian Football Association, Tottenham Hotspur FC", "NBA China Games", "Carlos Alcaraz, Laver Cup"],
];
const BRIEF_CRITERIA = [
  "Integration inside the partner's business",
  "Clear line to revenue and payment volume",
  "Hospitality at the centre",
  "Access to the partner's commercial network",
  "Reach in Europe, North America and APAC (incl. Japan, India)",
];
const ROUTES = [
  { n: 1, type: "Team", name: "Alpine F1 Team" },
  { n: 2, type: "Team", name: "Scuderia Ferrari" },
  { n: 3, type: "Driver", name: "Max Verstappen" },
];

// ------------------------------------------------------------------ slides
async function build() {
  await defineLayouts();
  // 1 Cover ------------------------------------------------------------
  pres.addSection({ title: "Introduction" });
  {
    const s = pres.addSlide({ masterName: "COVER", sectionTitle: "Introduction" });
    s.addText("PARTNERSHIP PROPOSAL", { placeholder: "eyebrow" });
    s.addText([{ text: "Adyen ×", options: { breakLine: true } }, { text: "Formula 1", options: { color: C.accent1 } }], { placeholder: "title" });
    s.addText("Why F1 is the right platform for Adyen, and how to win in it", { placeholder: "subtitle" });
    s.addText([{ text: "Prepared for " }, { text: "[ADD: name, Chairman]", options: { italic: true } }, { text: "  ·  " },
      { text: "[ADD: date]", options: { italic: true } }], { placeholder: "meta" });
    s.addNotes("Cover. Add a hero photo in the right-hand picture placeholder (click the icon). Replace the [ADD] fields with the chairman's name and meeting date.");
  }

  // 2 Executive summary -------------------------------------------------
  {
    const s = content("CONTENT", "Introduction", "Executive summary",
      t("F1 gives Adyen a **global, enterprise-grade stage**, and payments is now one of its most contested categories"),
      "Source: GWI; GlobalData; F1; Adyen; SPORTFIVE analysis. See Sources & notes.",
      "The one-page story for the chairman. Left: why F1 (four proof points, all from the BI work). Right: the recommendation and the ask, to be completed once the preferred route is agreed.");
    const rows = [
      ["625M", "A platform in growth", "F1 followers in 2026, up 30.8% since 2022. New sponsorship deal value is up 165% since 2020."],
      ["#1", "The audience Adyen sells to", "F1 ranks #1 of five major sports on all five Adyen audiences, from senior decision-makers to early tech adopters."],
      ["457M", "Where Adyen does business", "F1 fans across Adyen's 22 office markets, 13 of which host a 2027 race. India +95% and Japan +41% since 2022."],
      ["4", "A contested category", "Payment brands already partner F1 teams: Stripe, Airwallex, Mastercard and Visa. Adyen is not yet in F1."],
    ];
    const y0 = 2.0, rh = 1.1;
    rows.forEach(([big, head, body], i) => {
      const y = y0 + i * rh;
      if (i) s.addShape(S.LINE, { x: L, y: y - 0.06, w: 7.3, h: 0, line: { color: C.accent4, width: 0.75 } });
      s.addText(big, { x: L, y: y + 0.05, w: 1.75, h: 0.75, fontSize: 34, color: C.text1, margin: 0, valign: "top", isTextBox: true });
      s.addText([{ text: head, options: { bold: true, color: C.text1, breakLine: true } }, { text: body, options: { color: C.text2 } }],
        { x: L + 1.85, y: y + 0.05, w: 5.45, h: 0.95, fontSize: 13, margin: 0, valign: "top", paraSpaceAfter: 2, isTextBox: true });
    });
    const x = 8.35, w = R - x, y = 2.0, h = 4.55;
    card(s, x, y, w, h, C.text1, "Recommendation card");
    label(s, "Our recommendation", x + 0.35, y + 0.3, w - 0.7, C.accent1);
    ph(s, x + 0.35, y + 0.65, w - 0.7, 0.75, "Recommended asset and one-line rationale", { dark: true, size: 13 });
    [["Where Adyen sits in the business", 1.65], ["Investment and term", 2.6], ["Decision needed today", 3.55]].forEach(([lab, dy]) => {
      label(s, lab, x + 0.35, y + dy, w - 0.7, C.accent4);
      ph(s, x + 0.35, y + dy + 0.3, w - 0.7, 0.5, "One line", { dark: true, size: 12, align: "left" });
    });
  }

  // 3 Divider: Why F1 -------------------------------------------------------
  pres.addSection({ title: SECTIONS[0] });
  divider(1, "Why Formula 1", "Growth, audience and footprint: what the data says about F1 as a platform for Adyen",
    "Section 1 answers 'why F1 at all?' before any asset is discussed.");

  // 4 Growth --------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why Formula 1 · Growth",
      t("F1 is growing in **audience and in commercial value**"),
      "Source: GWI (global audience, followers); GlobalData (new sponsorship deals only, excl. renewals). 2026 YTD: $1.91B across 139 deals, year incomplete.",
      "Audience: 478.0M (2022) to 625.3M (2026), +30.8%, +147.3M followers; +8.3% vs 2025.\nSponsorship: total value of NEW deals, not annual sponsorship revenue. $0.89B (2020) to $2.37B (2025), +165.3%. 125 new deals in 2025 (+28.9% vs 2020). Average annual value $2.21M to $5.78M (+161.5%). 2020-2025 used because 2026 is incomplete.");
    const cards = [
      { x: L, head: "Global F1 audience", big: "+30.8%", sub: "2022–2026 · 147.3M additional followers", d: AUDIENCE,
        fmt: '0.0"M"', note: "625.3M followers in 2026, +8.3% vs 2025" },
      { x: L + CW / 2 + 0.15, head: "New F1 sponsorship deal value", big: "+165.3%", sub: "2020–2025 · new deals only, excludes renewals", d: DEALS,
        fmt: '"$"0.00"B"', note: "125 new deals in 2025 (+28.9% vs 2020)" },
    ];
    const cw = CW / 2 - 0.15;
    for (const c of cards) {
      card(s, c.x, 2.0, cw, 3.95);
      label(s, c.head, c.x + 0.3, 2.2, cw - 0.6);
      s.addText(c.big, { x: c.x + 0.3, y: 2.5, w: 2.4, h: 0.6, fontSize: 32, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(c.sub, { x: c.x + 2.55, y: 2.6, w: cw - 2.85, h: 0.45, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
      const n = c.d.values.length;
      s.addChart(pres.charts.BAR, [{ name: c.head, labels: c.d.years, values: c.d.values }], {
        x: c.x + 0.15, y: 3.15, w: cw - 0.3, h: 2.35, barDir: "col", ...chartBase(),
        chartColors: c.d.values.map((_, i) => (i === n - 1 ? HEX.green : HEX.context)),
        dataLabelFormatCode: c.fmt, valAxisMinVal: 0,
      });
      s.addText(c.note, { x: c.x + 0.3, y: 5.5, w: cw - 0.6, h: 0.3, fontSize: 11, color: C.text2, margin: 0, isTextBox: true });
    }
    soWhat(s, "brands are paying more to be in F1. The average annual value of a new deal rose from **$2.21M in 2020 to $5.78M in 2025**.");
  }

  // 5 Audience fit ---------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why Formula 1 · Audience",
      t("F1 is the strongest sport for **every audience Adyen sells to**"),
      "Source: GWI. Affinity index; ranking covers the five sports assessed. Benchmark per GWI methodology.",
      "Indices are not percentages. Definitions: high income = highest income segment; owners/founders = own or founded a business; senior decision-makers = influence over workplace purchasing; large company employees = companies with 1,001-5,000 employees; early tech adopters = among the first to adopt new technologies.\nNext-best sport: tennis on four measures, cycling on early tech adopters.");
    const cols = ["High income", "Owners / founders", "Senior decision-makers", "Large-company employees", "Early tech adopters"];
    const meaning = ["Premium consumers", "Merchant owners", "Enterprise buyers", "Enterprise accounts", "New-payment adopters"];
    const hdr = (txt, o = {}) => ({ text: txt, options: { bold: true, color: C.background1, fill: { color: C.text1 }, align: "center",
      valign: "middle", fontSize: 11, ...o } });
    const rows = [
      [hdr("Sport", { align: "left" }), ...cols.map((c) => hdr(c))],
      [{ text: "Means for Adyen", options: { italic: true, color: C.text2, fill: { color: C.background2 }, fontSize: 10 } },
        ...meaning.map((m) => ({ text: m, options: { italic: true, color: C.text2, fill: { color: C.background2 }, align: "center", fontSize: 10 } }))],
      ...AFFINITY.map((r, i) => r.map((v, j) => ({
        text: j === 0 ? v : v.toFixed(1),
        options: { bold: i === 0, color: C.text1, align: j === 0 ? "left" : "center", valign: "middle", fontSize: j === 0 ? 12 : 13,
          fill: { color: i === 0 ? C.accent6 : C.background1 } },
      }))),
    ];
    s.addTable(rows, { x: L, y: 2.0, w: 8.35, colW: [1.6, 1.35, 1.35, 1.35, 1.35, 1.35], rowH: [0.62, 0.42, 0.52, 0.52, 0.52, 0.52, 0.52],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.04, 0.08, 0.04, 0.08], objectName: "Affinity table" });
    s.addText("F1 ranks #1 on all five measures. Higher index = stronger over-representation among the sport's fans.",
      { x: L, y: 5.75, w: 8.35, h: 0.3, fontSize: 11, color: C.text2, margin: 0, isTextBox: true });
    const stats = [["237.9", "Early tech adopters", "31% above the next-best sport (cycling, 181.8)"],
      ["166.6", "Senior decision-makers", "12% above the next-best sport (tennis, 148.1)"]];
    stats.forEach(([big, head, body], i) => {
      const x = 9.25, y = 2.0 + i * 1.98, w = R - 9.25, h = 1.83;
      card(s, x, y, w, h);
      s.addText(big, { x: x + 0.3, y: y + 0.2, w: w - 0.6, h: 0.7, fontSize: 36, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText([{ text: head, options: { bold: true, color: C.text1, breakLine: true } }, { text: body, options: { color: C.text2 } }],
        { x: x + 0.3, y: y + 0.92, w: w - 0.6, h: 0.8, fontSize: 12, margin: 0, isTextBox: true, valign: "top" });
    });
    soWhat(s, "F1 is the only sport of the five that leads on **every audience Adyen needs**, from enterprise buyers to the consumers adopting new ways to pay.");
  }

  // 6 Footprint --------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why Formula 1 · Footprint",
      t("F1 races **where Adyen already does business**"),
      "Source: F1 2027 calendar and Adyen office list as supplied to SPORTFIVE (calendar not independently confirmed).",
      REGIONS.map(([r, o, rc]) => `${r}: offices ${o.join(", ")}; races ${rc.length ? rc.join(", ") : "none"}.`).join("\n"));
    const cx = [L, L + 1.85, L + 4.75, L + 7.35], hy = 2.0, ry = 2.42, rh = 0.5;
    ["Region", "Adyen offices", "F1 races 2027", "Office city with a race"].forEach((h, i) =>
      label(s, h, cx[i], hy, i === 3 ? 1.75 : 2.6));
    REGIONS.forEach(([region, offices, races, shared], i) => {
      const y = ry + i * rh;
      s.addShape(S.LINE, { x: L, y, w: 9.1, h: 0, line: { color: C.accent4, width: 0.75 } });
      s.addText(region, { x: cx[0], y, w: 1.8, h: rh, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      const mark = (n, x0, shape, color) => {
        s.addText(String(n), { x: x0, y, w: 0.35, h: rh, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
        for (let k = 0; k < n; k++)
          s.addShape(shape, { x: x0 + 0.4 + k * 0.19, y: y + rh / 2 - 0.065, w: 0.13, h: 0.13, fill: { color }, line: { color, width: 0 } });
      };
      mark(offices.length, cx[1], S.OVAL, C.accent1);
      mark(races.length, cx[2], S.DIAMOND, C.text1);
      s.addText(shared, { x: cx[3], y, w: 1.8, h: rh, fontSize: 12, bold: shared !== "—" && shared !== "No race",
        color: shared === "—" || shared === "No race" ? C.accent3 : C.accent2, margin: 0, valign: "middle", isTextBox: true });
    });
    s.addShape(S.LINE, { x: L, y: ry + REGIONS.length * rh, w: 9.1, h: 0, line: { color: C.accent4, width: 0.75 } });
    const ly = ry + REGIONS.length * rh + 0.15;
    s.addShape(S.OVAL, { x: L, y: ly + 0.06, w: 0.13, h: 0.13, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
    s.addText("Adyen office", { x: L + 0.2, y: ly, w: 1.3, h: 0.25, fontSize: 10, color: C.text2, margin: 0, isTextBox: true });
    s.addShape(S.DIAMOND, { x: L + 1.5, y: ly + 0.06, w: 0.13, h: 0.13, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
    s.addText("F1 race weekend", { x: L + 1.7, y: ly, w: 1.6, h: 0.25, fontSize: 10, color: C.text2, margin: 0, isTextBox: true });
    const stats = [["24", "Grands Prix on the 2027 calendar"], ["28", "Adyen offices worldwide"], ["7 of 8", "regions where Adyen has an office host a race"]];
    stats.forEach(([big, body], i) => {
      const x = 10.05, w = R - x, y = 2.0 + i * 1.5, h = 1.35;
      card(s, x, y, w, h);
      s.addText(big, { x: x + 0.3, y: y + 0.15, w: w - 0.6, h: 0.6, fontSize: 30, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(body, { x: x + 0.3, y: y + 0.78, w: w - 0.6, h: 0.5, fontSize: 12, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
  }

  // 7 Priority markets ---------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why Formula 1 · Priority markets",
      t("457M F1 fans live in Adyen's markets, and **India and Japan are accelerating**"),
      "Source: GWI (F1 audience by market, 2026 vs 2022); Adyen (office markets). Growth rates as reported.",
      "All 22 Adyen office markets: combined F1 audience 457.2M in 2026 vs 342.3M in 2022 (+33.6%). 13 of 22 host a 2027 race (59%). Chart shows the 11 largest; the other 11 (Malaysia, Canada, Australia, Poland, Netherlands, UAE, Belgium, Czechia, Sweden, Singapore, Hong Kong) add 34.4M. Fastest growth: India +94.9%, Australia +85.2%, US +74.3%, Canada +62.1%.");
    s.addShape(S.RECTANGLE, { x: L, y: 2.05, w: 0.14, h: 0.14, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
    s.addText("Hosts a 2027 race", { x: L + 0.22, y: 1.99, w: 1.8, h: 0.26, fontSize: 10.5, color: C.text2, margin: 0, isTextBox: true });
    s.addShape(S.RECTANGLE, { x: L + 2.0, y: 2.05, w: 0.14, h: 0.14, fill: { color: HEX.context }, line: { color: HEX.context, width: 0 } });
    s.addText("No race in 2027", { x: L + 2.22, y: 1.99, w: 1.8, h: 0.26, fontSize: 10.5, color: C.text2, margin: 0, isTextBox: true });
    s.addText("F1 audience, millions (growth 2022–2026)", { x: L + 4.2, y: 1.99, w: 3.4, h: 0.26, fontSize: 10.5, color: C.text2,
      margin: 0, align: "right", isTextBox: true });
    s.addChart(pres.charts.BAR, [{ name: "F1 audience (M)", labels: MARKETS.map(([m, , g]) => `${m}  (${g})`), values: MARKETS.map((m) => m[1]) }], {
      x: L - 0.1, y: 2.3, w: 7.8, h: 3.95, barDir: "bar", ...chartBase(), catAxisOrientation: "maxMin", barGapWidthPct: 45,
      chartColors: MARKETS.map((m) => (m[3] ? HEX.green : HEX.context)), dataLabelFormatCode: "0.0", catAxisLabelFontSize: 10.5,
      dataLabelFontSize: 10.5, valAxisMinVal: 0, valAxisMaxVal: 140,
    });
    s.addText("Plus 11 further Adyen markets: 34.4M fans.", { x: L, y: 6.3, w: 7.6, h: 0.28, fontSize: 10.5, color: C.text2, margin: 0, isTextBox: true });
    const stats = [
      ["457.2M", "F1 fans across Adyen's 22 office markets", "+33.6% since 2022; 13 of the 22 markets host a 2027 race.", false],
      ["India · 117.4M", "+94.9% since 2022", "The fastest growth of any Adyen office market, with no Grand Prix on the calendar.", true],
      ["Japan · 7.1M", "+41.2% since 2022", "A priority market for Adyen, home of the Suzuka Grand Prix.", true],
    ];
    stats.forEach(([big, head, body, priority], i) => {
      const x = 8.75, w = R - x, y = 2.0 + i * 1.53, h = 1.4;
      card(s, x, y, w, h);
      s.addText(big, { x: x + 0.3, y: y + 0.14, w: w - 0.6, h: 0.5, fontSize: 24, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      if (priority) {
        s.addShape(S.ROUNDED_RECTANGLE, { x: x + w - 1.55, y: y + 0.18, w: 1.3, h: 0.28, rectRadius: 0.14, fill: { color: C.accent6 },
          line: { color: C.accent6, width: 0 } });
        s.addText("PRIORITY MARKET", { x: x + w - 1.55, y: y + 0.18, w: 1.3, h: 0.28, fontSize: 8, bold: true, color: C.accent2,
          align: "center", valign: "middle", margin: 0, isTextBox: true });
      }
      s.addText([{ text: head, options: { bold: true, color: C.text1, breakLine: true } }, { text: body, options: { color: C.text2 } }],
        { x: x + 0.3, y: y + 0.65, w: w - 0.6, h: 0.7, fontSize: 11.5, margin: 0, isTextBox: true, valign: "top" });
    });
  }

  // 8 So what for Adyen ---------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why Formula 1 · What it means for Adyen",
      t("Why F1 makes sense for Adyen, **in six data points**"),
      "Source: GWI; GlobalData; F1; Adyen; SPORTFIVE analysis.",
      "This is the synthesis of section 1. Each card pairs something Adyen needs from a partnership with the evidence that F1 delivers it.");
    const items = [
      ["FiBriefcase", "Reach enterprise buyers", "166.6", "Senior decision-maker index, the highest of the five sports assessed"],
      ["FiZap", "Lead on innovation", "237.9", "Early tech adopter index, 31% above the next-best sport"],
      ["FiGlobe", "Grow in priority markets", "457M", "F1 fans across Adyen's 22 office markets, +33.6% since 2022"],
      ["FiCalendar", "Host clients where they are", "13 of 22", "Adyen office markets host a Grand Prix in 2027"],
      ["FiFlag", "Keep pace with the category", "4", "Payment brands already in F1: Stripe, Airwallex, Mastercard, Visa"],
      ["FiTrendingUp", "Invest in a rising asset", "$5.78M", "Average annual value of a new F1 deal in 2025, up from $2.21M in 2020"],
    ];
    const cw = (CW - 0.6) / 3, ch = 2.15;
    for (const [i, [ic, need, big, body]] of items.entries()) {
      const x = L + (i % 3) * (cw + 0.3), y = 2.0 + Math.floor(i / 3) * (ch + 0.25);
      card(s, x, y, cw, ch);
      await iconDot(s, ic, x + 0.3, y + 0.28, 0.46);
      s.addText(need, { x: x + 0.9, y: y + 0.28, w: cw - 1.1, h: 0.46, fontSize: 13, bold: true, color: C.text1, margin: 0,
        valign: "middle", isTextBox: true });
      s.addText(big, { x: x + 0.3, y: y + 0.88, w: cw - 0.6, h: 0.55, fontSize: 28, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(body, { x: x + 0.3, y: y + 1.45, w: cw - 0.6, h: 0.6, fontSize: 12, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    }
  }

  // 9 Divider: Competitive landscape ---------------------------------------------
  pres.addSection({ title: SECTIONS[1] });
  divider(2, "Competitive landscape", "Who is already using sport, and F1 in particular, to win in payments",
    "Section 2 shows the category is moving: competitors are in, and the benchmark has shifted from logos to integration.");

  // 10 Payments in F1 ---------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[1], "02 Competitive landscape · Payments in F1",
      t("Payments is one of F1's **most contested categories**"),
      "Source: SPORTFIVE analysis. Team names as used in the BI scan.",
      "Stripe and Airwallex compete with Adyen directly. Visa and Mastercard are card schemes and Adyen partners; Mastercard and Airwallex already sit side by side at McLaren, which shows scheme and platform partners can co-exist.");
    const pts = [
      ["FiLayers", "Four payment brands already partner F1 teams", "Two are Adyen competitors (Stripe, Airwallex); two are card schemes (Mastercard, Visa)."],
      ["FiLink", "Integration is the new benchmark", "Airwallex sits inside McLaren's business, not just on the car."],
      ["FiShield", "Card schemes are partners, not blockers", "Visa and Mastercard partner Adyen; Mastercard and Airwallex already co-exist at McLaren."],
    ];
    for (const [i, [ic, head, body]] of pts.entries()) {
      const y = 2.05 + i * 1.5;
      await iconDot(s, ic, L, y, 0.46);
      s.addText([{ text: head, options: { bold: true, color: C.text1, breakLine: true } }, { text: body, options: { color: C.text2 } }],
        { x: L + 0.65, y: y - 0.02, w: 3.85, h: 1.3, fontSize: 13, margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 3 });
    }
    const brands = [
      ["Stripe", "Mercedes-AMG Petronas F1 Team", "Competitor"],
      ["Airwallex", "McLaren F1 Team", "Competitor"],
      ["Mastercard", "McLaren Mastercard F1 Team", "Adyen partner"],
      ["Visa", "Red Bull", "Adyen partner"],
    ];
    const gx = 5.45, gw = (R - gx - 0.3) / 2, gh = 1.62;
    brands.forEach(([name, team, kind], i) => {
      const x = gx + (i % 2) * (gw + 0.3), y = 2.0 + Math.floor(i / 2) * (gh + 0.28);
      card(s, x, y, gw, gh);
      const comp = kind === "Competitor";
      s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.3, y: y + 0.25, w: 1.35, h: 0.28, rectRadius: 0.14,
        fill: { color: comp ? C.text1 : C.background1 }, line: { color: comp ? C.text1 : C.accent1, width: 1 } });
      s.addText(kind.toUpperCase(), { x: x + 0.3, y: y + 0.25, w: 1.35, h: 0.28, fontSize: 8, bold: true, align: "center", valign: "middle",
        color: comp ? C.background1 : C.accent2, margin: 0, isTextBox: true });
      s.addText(name, { x: x + 0.3, y: y + 0.65, w: gw - 0.6, h: 0.45, fontSize: 20, bold: true, color: C.text1, margin: 0, isTextBox: true });
      s.addText(team, { x: x + 0.3, y: y + 1.1, w: gw - 0.6, h: 0.35, fontSize: 12, color: C.text2, margin: 0, isTextBox: true });
    });
    const ay = 2.0 + 2 * (gh + 0.28);
    s.addShape(S.ROUNDED_RECTANGLE, { x: gx, y: ay, w: R - gx, h: 0.82, rectRadius: 0.08, fill: { color: C.accent6 },
      line: { color: C.accent1, width: 1.25, dashType: "dash" } });
    s.addImage({ path: A("adyen_green.png"), x: gx + 0.3, y: ay + 0.29, w: 0.75, h: 0.24 });
    s.addText([{ text: "Not yet in F1.  ", options: { bold: true, color: C.text1 } }, ...add("Adyen's F1 home and the role it plays", 13)],
      { x: gx + 1.3, y: ay, w: R - gx - 1.55, h: 0.82, fontSize: 13, margin: 0, valign: "middle", isTextBox: true });
  }

  // 11 Competitors across sport ---------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[1], "02 Competitive landscape · Competitors in sport",
      t("Adyen's competitors are already buying into sport, but **only two have committed to F1**"),
      "Source: SPORTFIVE BI competitor scan (not exhaustive). Property types vary (teams, leagues, venues, athletes); no equivalence of rights, fees or exclusivity implied.",
      "Counts by column: F1 2, football 11, US leagues & college 12, other sport & venues 7 (32 properties in total). Football includes MLS clubs. 'Other' covers golf, tennis, Australian football and venues.");
    const counts = [2, 11, 12, 7];
    const heads = ["F1", "Football", "US leagues & college", "Other & venues"];
    const hcell = (txt, f1) => ({ text: txt, options: { bold: true, color: f1 ? C.text1 : C.background1, fill: { color: f1 ? C.accent1 : C.text1 },
      fontSize: 11, valign: "middle" } });
    const rows = [[hcell("Competitor"), ...heads.map((h, i) => hcell(`${h}  (${counts[i]})`, i === 0))],
      ...COMPETITORS.map(([name, ...cells]) => [
        { text: name, options: { bold: true, color: C.text1, fontSize: 12, valign: "middle" } },
        ...cells.map((c, i) => ({ text: c || "—", options: { color: c ? (i === 0 ? C.text1 : C.text2) : C.accent4, bold: i === 0 && !!c,
          fontSize: 10.5, valign: "middle", fill: { color: i === 0 ? C.accent6 : C.background1 } } })),
      ])];
    s.addTable(rows, { x: L, y: 2.0, w: CW, colW: [1.6, 2.45, 3.1, 3.1, 1.88],
      rowH: [0.42, 0.42, 0.42, 0.5, 0.42, 0.68, 0.42, 0.5], border: { type: "solid", pt: 0.75, color: C.accent4 },
      margin: [0.04, 0.1, 0.04, 0.1], objectName: "Competitor table" });
    soWhat(s, "competitor money is spread across football and US leagues. In F1, **only Stripe and Airwallex have team partnerships**: the category is still open for Adyen to lead.", 6.22);
  }

  // 12 Airwallex x McLaren ---------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[1], "02 Competitive landscape · The benchmark",
      t("The model to beat: Airwallex × McLaren, **integration not a logo**"),
      "Source: SPORTFIVE analysis.",
      "Use this as the benchmark Mark's brief sets: a payments brand inside the team's business. Add Airwallex results if you have verified figures.");
    ph(s, L, 2.0, 4.55, 4.6, "Image: Airwallex × McLaren activation");
    const x = 5.55, w = R - x;
    label(s, "What Airwallex did", x, 2.0, w);
    const did = [
      "Positioned the deal as business integration, embedding its financial solutions in the partner's operations.",
      "Activated the IP across content, events, hospitality and performance marketing.",
      "Built one B2B sports platform: McLaren in F1, plus Arsenal FC, San Francisco Giants and Essendon FC.",
    ];
    did.forEach((d, i) => {
      const y = 2.35 + i * 0.62;
      s.addShape(S.OVAL, { x, y: y + 0.02, w: 0.32, h: 0.32, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
      s.addText(String(i + 1), { x, y: y + 0.02, w: 0.32, h: 0.32, fontSize: 11, bold: true, color: C.background1, align: "center",
        valign: "middle", margin: 0, isTextBox: true });
      s.addText(d, { x: x + 0.5, y, w: w - 0.5, h: 0.55, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
    });
    ph(s, x, 4.25, w, 0.45, "Results Airwallex has reported (volumes, customers, pipeline)", { size: 11.5, align: "left" });
    card(s, x, 4.9, w, 1.7, C.accent6, "Lessons");
    label(s, "What it means for Adyen", x + 0.3, 5.05, w - 0.6, C.accent2);
    s.addText([
      { text: "Lead with where Adyen sits inside the partner's business, not the logo.", options: { bullet: true, breakLine: true } },
      { text: "Show a clear line to revenue and payment volume.", options: { bullet: true, breakLine: true } },
      { text: "Put hospitality at the centre, connecting people across the partner's ecosystem.", options: { bullet: true } },
    ], { x: x + 0.3, y: 5.35, w: w - 0.6, h: 1.15, fontSize: 13, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 4, isTextBox: true });
  }

  // 13 Divider: Opportunities ------------------------------------------------------------------
  pres.addSection({ title: SECTIONS[2] });
  divider(3, "The opportunities", "Three routes into F1: two teams and one driver",
    "Section 3 is for the asset content your team will add. Each route uses the same structure so the chairman can compare like for like.");

  // 14 Routes at a glance ------------------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[2], "03 The opportunities · Overview",
      t("Three routes into F1 for Adyen"),
      "Source: [ADD]",
      "Fill each field in one line. Keep the same order as the detail slides that follow.");
    const cw = (CW - 0.6) / 3;
    ROUTES.forEach((r, i) => {
      const x = L + i * (cw + 0.3), y = 2.0;
      card(s, x, y, cw, 4.6);
      ph(s, x + 0.25, y + 0.25, cw - 0.5, 1.2, "Image or logo", { size: 11 });
      label(s, `Route ${r.n} · ${r.type}`, x + 0.3, y + 1.62, cw - 0.6, C.accent2);
      s.addText(r.name, { x: x + 0.3, y: y + 1.88, w: cw - 0.6, h: 0.45, fontSize: 20, bold: true, color: C.text1, margin: 0, isTextBox: true });
      ["The opportunity", "Where Adyen sits in the business", "Indicative investment", "Status"].forEach((f, k) => {
        const fy = y + 2.45 + k * 0.52;
        s.addText([{ text: f + "  ", options: { bold: true, color: C.text1, breakLine: true } }, ...add("one line", 11)],
          { x: x + 0.3, y: fy, w: cw - 0.6, h: 0.5, fontSize: 11, margin: 0, isTextBox: true, valign: "top" });
      });
    });
  }

  // 15-17 Route detail --------------------------------------------------------------------------
  for (const r of ROUTES) {
    const s = content("CONTENT_PHOTO", SECTIONS[2], `03 The opportunities · Route ${r.n} · ${r.type}`,
      [{ text: r.name + ": " }, { text: "[ADD: one-line positioning]", options: { color: C.accent3, italic: true } }],
      "Source: [ADD]",
      `Detail slide for ${r.name}. Add a photo on the left, three headline numbers, the case for the asset, and an honest read against each of the five criteria from Adyen's brief.`);
    const x = 5.35, w = R - x;
    const tw = (w - 0.5) / 3;
    for (let k = 0; k < 3; k++) {
      const tx = x + k * (tw + 0.25);
      card(s, tx, 2.0, tw, 1.25);
      s.addText("[ADD]", { x: tx + 0.25, y: 2.12, w: tw - 0.5, h: 0.55, fontSize: 24, color: C.accent3, margin: 0, isTextBox: true, valign: "top" });
      s.addText(add("Headline number and label", 11), { x: tx + 0.25, y: 2.7, w: tw - 0.5, h: 0.45, margin: 0, isTextBox: true, valign: "top" });
    }
    const hw = (w - 0.35) / 2;
    label(s, "Why this asset", x, 3.55, hw);
    for (let k = 0; k < 3; k++) ph(s, x, 3.9 + k * 0.88, hw, 0.72, "Reason " + (k + 1), { size: 11.5, align: "left" });
    const fx = x + hw + 0.35;
    label(s, "Fit with Adyen's brief", fx, 3.55, hw);
    BRIEF_CRITERIA.forEach((c, k) => {
      const y = 3.9 + k * 0.53;
      card(s, fx, y, hw, 0.45);
      s.addText(c, { x: fx + 0.2, y, w: hw - 1.0, h: 0.45, fontSize: 10.5, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      s.addText("[ ● ◐ ○ ]", { x: fx + hw - 0.85, y, w: 0.75, h: 0.45, fontSize: 10.5, color: C.accent3, align: "right", margin: 0,
        valign: "middle", isTextBox: true });
    });
  }

  // 18 Divider: Recommendation ------------------------------------------------------------------
  pres.addSection({ title: SECTIONS[3] });
  divider(4, "Our recommendation", "The preferred route, how Adyen integrates, the rights, and the investment",
    "Section 4 closes the case: which asset, why, where Adyen sits in the business, what it costs and what happens next.");

  // 19 Why we recommend -------------------------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[3], "04 Recommendation · Assessment",
      [{ text: "Why we recommend " }, { text: "[ADD: asset]", options: { color: C.accent1 } }],
      "Source: SPORTFIVE assessment against Adyen's partnership brief.",
      "Rate each route ● strong, ◐ partial, ○ weak, with a few words of evidence in each cell. Criteria rows 1-5 come straight from Adyen's brief.");
    const crit = [...BRIEF_CRITERIA, "Fits the investment envelope", "Payments category available"];
    const hc = (txt) => ({ text: txt, options: { bold: true, color: C.background1, fill: { color: C.text1 }, align: "center", valign: "middle", fontSize: 12 } });
    const rows = [[{ ...hc("Criterion"), options: { ...hc("").options, align: "left" } }, ...ROUTES.map((r) => hc(r.name))],
      ...crit.map((c, i) => [
        { text: c, options: { color: C.text1, fontSize: 12, valign: "middle", bold: i < 5 ? false : false } },
        ...ROUTES.map(() => ({ text: "[ADD ● ◐ ○ + evidence]", options: { italic: true, color: C.accent3, fontSize: 10.5, align: "center", valign: "middle" } })),
      ])];
    rows[0][0].text = "Criterion";
    s.addTable(rows, { x: L, y: 2.0, w: CW, colW: [4.63, 2.5, 2.5, 2.5], rowH: [0.48, ...crit.map(() => 0.44)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.04, 0.12, 0.04, 0.12], objectName: "Assessment table" });
    s.addText([{ text: "●", options: { color: C.accent1 } }, { text: " strong fit    " }, { text: "◐", options: { color: C.accent1 } },
      { text: " partial    " }, { text: "○", options: { color: C.accent1 } }, { text: " weak" }],
    { x: L, y: 5.6, w: 5, h: 0.3, fontSize: 11, color: C.text2, margin: 0, isTextBox: true });
    card(s, L, 6.02, CW, 0.62, C.text1, "Recommendation strip");
    s.addText([{ text: "Our recommendation  ", options: { bold: true, color: C.accent1 } },
      { text: "[ADD: asset], because [ADD: one-line rationale]", options: { italic: true, color: C.background1 } }],
    { x: L + 0.3, y: 6.02, w: CW - 0.6, h: 0.62, fontSize: 14, margin: 0, valign: "middle", isTextBox: true });
  }

  // 20 Business integration -----------------------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[3], "04 Recommendation · Business integration",
      [{ text: "Where Adyen sits " }, { text: "inside [ADD: asset]'s business", options: { color: C.accent1 } }],
      "Source: [ADD]",
      "Integration first, not a logo deal. Replace each [ADD] with the specific commerce flows, KPIs, races and partners agreed with the rights-holder.");
    const steps = [
      ["FiCreditCard", "Power", "Adyen runs the partner's payments across ticketing, e-commerce, merchandise and hospitality.", "Which flows Adyen powers"],
      ["FiBarChart2", "Prove", "Live volumes and conversion data become a flagship, client-facing case study.", "KPIs to report"],
      ["FiUsers", "Host", "Hospitality at the centre, connecting clients across the partner's ecosystem.", "Races, guests, format"],
      ["FiShare2", "Connect", "Access to the partner's commercial network turns into qualified pipeline.", "Target partners and accounts"],
    ];
    const sw = (CW - 0.9) / 4, y = 2.25, h = 3.55;
    s.addShape(S.LINE, { x: L + sw / 2, y: y + 0.45, w: CW - sw, h: 0, line: { color: C.accent1, width: 2 } });
    for (const [i, [ic, name, body, ph1]] of steps.entries()) {
      const x = L + i * (sw + 0.3);
      card(s, x, y + 0.95, sw, h - 0.95);
      await iconDot(s, ic, x + sw / 2 - 0.45, y, 0.9);
      s.addText(`${i + 1}  ${name}`, { x: x + 0.25, y: y + 1.15, w: sw - 0.5, h: 0.4, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
      s.addText(body, { x: x + 0.25, y: y + 1.6, w: sw - 0.5, h: 0.95, fontSize: 12.5, color: C.text2, margin: 0, valign: "top", isTextBox: true });
      ph(s, x + 0.2, y + h - 0.85, sw - 0.4, 0.65, ph1, { size: 11 });
    }
    soWhat(s, "**integration first, not a logo deal.** Every route is tested on how deeply Adyen sits inside the partner's commercial operations.", 6.1);
  }

  // 21 Line to revenue ---------------------------------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[3], "04 Recommendation · Value",
      t("A clear line to **revenue and payment volume**"),
      "Source: Adyen case studies (FC Bayern, RSC Anderlecht); KPI targets [ADD].",
      "Left: the four numbers the chairman will ask for. Right: proof that Adyen already drives revenue in sport.");
    label(s, "How the partnership pays back", L, 2.0, 7);
    const kpis = [["FiDollarSign", "Payment volume processed", "€ through the partner's commerce"],
      ["FiTarget", "Qualified pipeline", "€ from hospitality and network introductions"],
      ["FiUsers", "C-level guests hosted", "# per season"],
      ["FiFileText", "Case studies and new logos", "# per season"]];
    const kw = (7.25 - 0.3) / 2, kh = 1.95;
    for (const [i, [ic, name, unit]] of kpis.entries()) {
      const x = L + (i % 2) * (kw + 0.3), y = 2.35 + Math.floor(i / 2) * (kh + 0.25);
      card(s, x, y, kw, kh);
      await iconDot(s, ic, x + 0.3, y + 0.28, 0.46);
      s.addText(name, { x: x + 0.9, y: y + 0.28, w: kw - 1.1, h: 0.46, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      s.addText("[ADD]", { x: x + 0.3, y: y + 0.9, w: kw - 0.6, h: 0.55, fontSize: 28, color: C.accent3, margin: 0, isTextBox: true, valign: "top" });
      s.addText(unit, { x: x + 0.3, y: y + 1.45, w: kw - 0.6, h: 0.35, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    }
    const x = 8.2, w = R - x;
    label(s, "Proof: Adyen already powers sport", x, 2.0, w);
    const proof = [
      ["+36.6%", "F&B revenue at RSC Anderlecht", "after moving the whole matchday fan journey to digital payments with Adyen."],
      ["1 platform", "for every FC Bayern payment", "across ticketing, retail, lifestyle and streaming, with new insight into fan behaviour."],
    ];
    proof.forEach(([big, head, body], i) => {
      const y = 2.35 + i * 2.2;
      card(s, x, y, w, 1.95, C.text1, "Proof card");
      s.addText(big, { x: x + 0.3, y: y + 0.22, w: w - 0.6, h: 0.6, fontSize: 30, color: C.accent1, margin: 0, isTextBox: true, valign: "top" });
      s.addText([{ text: head, options: { bold: true, color: C.background1, breakLine: true } }, { text: body, options: { color: C.accent4 } }],
        { x: x + 0.3, y: y + 0.9, w: w - 0.6, h: 0.95, fontSize: 12, margin: 0, isTextBox: true, valign: "top" });
    });
  }

  // 22 Rights overview ------------------------------------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[3], "04 Recommendation · Rights overview",
      [{ text: "Rights overview: " }, { text: "[ADD: asset]", options: { color: C.accent1 } }],
      "Source: [ADD: rights-holder proposal]. Provisional, subject to contract.",
      "Summarise the rights in one line per row. The right-hand column is the important one: tie every right back to Adyen's objectives.");
    const cats = ["Designation and category", "Brand visibility", "Content and IP", "Hospitality", "Access and network", "Term and investment"];
    const hc = (txt) => ({ text: txt, options: { bold: true, color: C.background1, fill: { color: C.text1 }, valign: "middle", fontSize: 12 } });
    const rows = [[hc("Category"), hc("What Adyen receives"), hc("Why it matters for Adyen")],
      ...cats.map((c) => [
        { text: c, options: { bold: true, color: C.text1, fontSize: 12, valign: "middle", fill: { color: C.background2 } } },
        { text: "[ADD]", options: { italic: true, color: C.accent3, fontSize: 11, valign: "middle" } },
        { text: "[ADD]", options: { italic: true, color: C.accent3, fontSize: 11, valign: "middle" } },
      ])];
    s.addTable(rows, { x: L, y: 2.0, w: CW, colW: [2.9, 4.8, 4.43], rowH: [0.48, ...cats.map(() => 0.66)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.04, 0.15, 0.04, 0.15], objectName: "Rights table" });
  }

  // 23 Investment & next steps --------------------------------------------------------------------------------------
  {
    const s = content("CONTENT", SECTIONS[3], "04 Recommendation · Investment and next steps",
      t("Investment and **next steps**"),
      "Source: Adyen budget guidance; GlobalData (average annual value of new F1 deals, 2025).",
      "Budget guidance from Adyen: $10M a year is defensible, $20M needs a very strong case, and a $5-7M option shows how it works. The dashed line marks the average annual value of a new F1 sponsorship deal in 2025 ($5.78M).");
    label(s, "Investment envelope (per year)", L, 2.0, 7);
    const opts = [["Prove the model", "$5–7M", 7, 5], ["Defensible core", "$10M", 10, null], ["Flagship", "$20M", 20, null]];
    const bx = L + 2.0, bw = 4.75, max = 20;
    opts.forEach(([name, val, hi, lo], i) => {
      const y = 2.45 + i * 1.12;
      s.addText(name, { x: L, y, w: 1.9, h: 0.42, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      s.addShape(S.RECTANGLE, { x: bx, y: y + 0.06, w: bw, h: 0.3, fill: { color: C.background2 }, line: { color: C.background2, width: 0 } });
      if (lo) s.addShape(S.RECTANGLE, { x: bx, y: y + 0.06, w: (bw * lo) / max, h: 0.3, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
      s.addShape(S.RECTANGLE, { x: bx + (lo ? (bw * lo) / max : 0), y: y + 0.06, w: (bw * (hi - (lo || 0))) / max, h: 0.3,
        fill: { color: lo ? C.accent6 : C.accent1 }, line: { color: C.accent1, width: lo ? 1 : 0 } });
      s.addText(val, { x: bx + (bw * hi) / max + 0.1, y, w: 0.9, h: 0.42, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      s.addText(add("What this level buys", 10.5), { x: bx, y: y + 0.45, w: bw, h: 0.3, margin: 0, isTextBox: true, valign: "top" });
    });
    const mx = bx + (bw * 5.78) / max;
    opts.forEach((_, i) => s.addShape(S.LINE, { x: mx, y: 2.45 + i * 1.12 - 0.02, w: 0, h: 0.46,
      line: { color: C.text1, width: 1.25, dashType: "dash" } }));
    s.addShape(S.LINE, { x: L, y: 5.72, w: 0.3, h: 0, line: { color: C.text1, width: 1.25, dashType: "dash" } });
    s.addText("Average annual value of a new F1 deal, 2025: $5.78M", { x: L + 0.4, y: 5.58, w: 5.5, h: 0.28, fontSize: 10.5,
      color: C.text2, margin: 0, isTextBox: true, valign: "middle" });

    const x = 8.2, w = R - x;
    label(s, "Next steps", x, 2.0, w);
    const steps = ["Chairman aligns on the preferred route", "Headline terms agreed with the rights-holder",
      "Contract and integration plan", "Launch"];
    s.addShape(S.LINE, { x: x + 0.14, y: 2.55, w: 0, h: 2.8, line: { color: C.accent4, width: 1.5 } });
    steps.forEach((st, i) => {
      const y = 2.4 + i * 0.92;
      s.addShape(S.OVAL, { x, y, w: 0.28, h: 0.28, fill: { color: C.accent1 }, line: { color: C.background1, width: 2 } });
      s.addText(st, { x: x + 0.5, y: y - 0.05, w: w - 0.5, h: 0.38, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });
      s.addText(add("date and owner", 11), { x: x + 0.5, y: y + 0.33, w: w - 0.5, h: 0.3, margin: 0, isTextBox: true, valign: "top" });
    });
    card(s, L, 6.1, CW, 0.58, C.text1, "Decision strip");
    s.addText([{ text: "Decision needed  ", options: { bold: true, color: C.accent1 } },
      { text: "[ADD: the approval you are asking the Chairman for]", options: { italic: true, color: C.background1 } }],
    { x: L + 0.3, y: 6.1, w: CW - 0.6, h: 0.58, fontSize: 14, margin: 0, valign: "middle", isTextBox: true });
  }

  // 24 Sources & notes ------------------------------------------------------------------------------------------------
  pres.addSection({ title: "Appendix" });
  {
    const s = content("CONTENT", "Appendix", "Appendix", t("Sources and notes"), "Prepared by SPORTFIVE for Adyen. Data as supplied; not independently verified unless stated.",
      "Keep this slide: it answers 'where does that number come from?' in the room.");
    const src = [
      ["GWI", "Global F1 audience 2022–2026; F1 audience by Adyen office market (2026 vs 2022); sport affinity indices for five Adyen-relevant audiences. Indices are not percentages; ranking covers the five sports assessed."],
      ["GlobalData", "F1 sponsorship, 2020–2025: new deals only, excluding renewals. Total deal value is not annual sponsorship revenue. 2026 is year-to-date ($1.91B, 139 deals)."],
      ["F1 calendar", "2027 race locations as supplied to SPORTFIVE; calendar not independently confirmed."],
      ["Adyen", "Office locations (28 cities, 22 markets); FC Bayern and RSC Anderlecht case studies; partnership brief."],
      ["SPORTFIVE", "Competitor sports-property scan (not exhaustive; no equivalence of rights, fees or exclusivity implied); payments presence in F1."],
    ];
    src.forEach(([h, b], i) => {
      const y = 2.0 + i * 0.86;
      if (i) s.addShape(S.LINE, { x: L, y: y - 0.1, w: CW, h: 0, line: { color: C.accent4, width: 0.75 } });
      s.addText(h, { x: L, y, w: 2.2, h: 0.7, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });
      s.addText(b, { x: L + 2.4, y, w: CW - 2.4, h: 0.7, fontSize: 12, color: C.text2, margin: 0, valign: "top", isTextBox: true });
    });
  }

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
