// Adyen x Formula 1: Chairman deck.
// v2: Adyen photography and brand palette; Adyen's brief and hypothesis up front; brand-value,
// partner-network and proof/credentials sections from the SPORTFIVE team deck; Max Verstappen and
// Alpine routes filled from their proposals; Ferrari left as structured placeholders.
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const Fi = require("react-icons/fi");
const SKILL = process.env.PPTX_SKILL || "/mnt/skills/public/pptx";
// let the theme helper (outside this folder) find this folder's pptxgenjs
process.env.NODE_PATH = [path.join(__dirname, "node_modules"), process.env.NODE_PATH].filter(Boolean).join(path.delimiter);
require("module").Module._initPaths();
const { applyTheme } = require(SKILL + "/scripts/apply_theme.js");

const OUT = process.argv[2] || "Adyen x F1 - Chairman deck.pptx";
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
const HEX = { navy: "00112C", green: "0ABF53", deep: "079A44", slate: "404B5F", muted: "8F97A3", context: "C9CFD6",
  hair: "E3E6EA", g1: "A9B0BA", g2: "C9CFD6", g3: "DDE1E6" };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Adyen x Formula 1";
pres.company = "SPORTFIVE";
const C = pres.SchemeColor;
const S = pres.shapes;

const W = 13.333, H = 7.5, L = 0.6, R = 12.733, CW = R - L;

// ------------------------------------------------------------------ icons and photos
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

const dims = {};
// place a photo cropped to fill the box (no distortion)
async function photo(s, file, x, y, w, h, alt) {
  if (!dims[file]) dims[file] = await sharp(A(file)).metadata();
  const { width, height } = dims[file];
  s.addImage({ path: A(file), x, y, w, h: (w * height) / width, sizing: { type: "cover", w, h }, altText: alt || "" });
}
// place an image at its own aspect ratio inside a box (fit)
async function fit(s, file, x, y, w, h, alt) {
  if (!dims[file]) dims[file] = await sharp(A(file)).metadata();
  const { width, height } = dims[file];
  const r = Math.min(w / width, h / height);
  const iw = width * r, ih = height * r;
  s.addImage({ path: A(file), x: x + (w - iw) / 2, y: y + (h - ih) / 2, w: iw, h: ih, altText: alt || "" });
  return { x: x + (w - iw) / 2, y: y + (h - ih) / 2, w: iw, h: ih };
}

// ------------------------------------------------------------------ layouts
let PHOTO_ICON;
const SECTIONS = ["Why Formula 1", "F1 as a business network", "Competitive landscape", "Proof and credentials",
  "The opportunities", "Recommendation"];
const SHORT = ["Why F1", "Business network", "Competition", "Proof", "Routes", "Recommendation"];

async function defineLayouts() {
  PHOTO_ICON = await icon("FiImage", "8F97A3");
  const footerObjects = (logo) => [
    { image: { x: 11.42, y: 6.98, w: 0.68, h: 0.22, path: A(logo), altText: "Adyen logo" } },
  ];

  pres.defineSlideMaster({
    title: "COVER",
    background: { color: C.text1 },
    objects: [
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

  // Full-bleed photo slides (brief, hypothesis): photo and overlay are added per slide, under the text.
  pres.defineSlideMaster({
    title: "STATEMENT",
    background: { color: C.text1 },
    objects: [
      { placeholder: { options: { name: "eyebrow", type: "body", x: L, y: 1.15, w: 11, h: 0.35, fontSize: 12, bold: true,
          color: C.accent1, charSpacing: 2, margin: 0, valign: "top" }, text: "EYEBROW" } },
      { placeholder: { options: { name: "title", type: "title", x: L, y: 1.55, w: 11.6, h: 1.9, fontSize: 36, color: C.background1,
          margin: 0, valign: "top", align: "left" }, text: "Statement" } },
      { image: { x: R - 1.12, y: 6.75, w: 1.12, h: 0.36, path: A("adyen_green.png"), altText: "Adyen logo" } },
    ],
  });

  pres.defineSlideMaster({
    title: "DIVIDER",
    background: { color: C.text1 },
    objects: [
      { placeholder: { options: { name: "num", type: "body", x: L, y: 1.6, w: 4, h: 1.3, fontSize: 80, bold: true,
          color: C.accent1, margin: 0, valign: "top" }, text: "01" } },
      { placeholder: { options: { name: "title", type: "title", x: L, y: 3.05, w: 7.2, h: 1.0, fontSize: 40, color: C.background1,
          margin: 0, valign: "top", align: "left" }, text: "Section title" } },
      { placeholder: { options: { name: "desc", type: "body", x: L, y: 4.15, w: 7.0, h: 1.1, fontSize: 18, color: C.accent4,
          margin: 0, valign: "top" }, text: "What this section answers" } },
      { image: { x: L, y: 0.55, w: 1.12, h: 0.36, path: A("adyen_green.png"), altText: "Adyen logo" } },
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
      { image: { x: 4.85 / 2 - 0.3, y: 3.2, w: 0.6, h: 0.6, data: PHOTO_ICON } },
      { text: { text: "Photo of the asset", options: { x: 0, y: 3.9, w: 4.85, h: 0.35, fontSize: 12, color: C.accent3, align: "center" } } },
      { placeholder: { options: { name: "photo", type: "image", x: 0, y: 0, w: 4.85, h: 7.5, color: C.text2 },
          text: "Add photo of the asset" } },
      ...contentObjects(5.35, R - 5.35),
    ],
    slideNumber,
  });
}

// ------------------------------------------------------------------ helpers
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

async function divider(n, title, desc, photoFile, notes) {
  const s = pres.addSlide({ masterName: "DIVIDER", sectionTitle: SECTIONS[n - 1] });
  await photo(s, photoFile, 8.33, 0, W - 8.33, H, "Section photo");
  s.addText(String(n).padStart(2, "0"), { placeholder: "num" });
  s.addText(title, { placeholder: "title" });
  s.addText(desc, { placeholder: "desc" });
  const span = 7.5, tw = span / SHORT.length;
  SHORT.forEach((name, i) => {
    const on = i === n - 1;
    s.addShape(S.LINE, { x: L + i * tw, y: 6.25, w: tw - 0.1, h: 0, line: { color: on ? C.accent1 : C.accent5, width: 2 } });
    s.addText([{ text: String(i + 1).padStart(2, "0"), options: { bold: true, color: on ? C.accent1 : C.accent3, breakLine: true } },
      { text: name, options: { color: on ? C.background1 : C.accent3, bold: on } }],
    { x: L + i * tw, y: 6.33, w: tw - 0.1, h: 0.6, fontSize: 9.5, margin: 0, isTextBox: true, valign: "top" });
  });
  if (notes) s.addNotes(notes);
  return s;
}

const hc = (txt, o = {}) => ({ text: txt, options: { bold: true, color: C.background1, fill: { color: C.text1 }, valign: "middle",
  fontSize: 11, ...o } });

const chartBase = () => ({
  catAxisLabelColor: HEX.slate, catAxisLabelFontSize: 11, catAxisLabelFontFace: "+mn-lt",
  catAxisLineShow: false, catGridLine: { style: "none" },
  valAxisHidden: true, valGridLine: { style: "none" }, valAxisLineShow: false,
  showValue: true, dataLabelColor: HEX.navy, dataLabelFontSize: 11, dataLabelFontFace: "+mn-lt", dataLabelFontBold: true,
  dataLabelPosition: "outEnd", showLegend: false, barGapWidthPct: 55,
});

// three text columns of rights: items are ["h", text] | ["kv", label, text] | ["b", text] | ["note", text]
function rightsColumns(s, cols, y, h, xs, ws, size = 10) {
  cols.forEach((items, ci) => {
    const runs = [];
    items.forEach((it, i) => {
      const last = i === items.length - 1;
      const gap = i === 0 ? 0 : it[0] === "h" ? 9 : 3;
      if (it[0] === "h") {
        runs.push({ text: it[1].toUpperCase(), options: { bold: true, color: C.accent2, fontSize: size, charSpacing: 0.5,
          paraSpaceBefore: gap, breakLine: !last } });
      } else if (it[0] === "kv") {
        runs.push({ text: it[1] + " ", options: { bold: true, color: C.text1, fontSize: size, paraSpaceBefore: gap } });
        runs.push({ text: it[2], options: { color: C.text2, fontSize: size, breakLine: !last } });
      } else if (it[0] === "b") {
        runs.push({ text: it[1], options: { color: C.text2, fontSize: size, bullet: { indent: 12 }, paraSpaceBefore: gap,
          breakLine: !last } });
      } else if (it[0] === "note") {
        runs.push({ text: it[1], options: { italic: true, color: C.accent3, fontSize: size - 1.5, paraSpaceBefore: 5, breakLine: !last } });
      }
    });
    s.addText(runs, { x: xs[ci], y, w: ws[ci], h, margin: 0, valign: "top", isTextBox: true, objectName: "Rights column " + (ci + 1) });
  });
}

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

// ------------------------------------------------------------------ data (team deck)
// Partners' combined revenue ($B) and top 3 partners by reported revenue, by team. Figures under review by the team.
const NETWORK = [
  ["Mercedes-AMG", 1040, "Microsoft, Meta, PepsiCo"], ["McLaren", 733, "Dell, Deloitte, Cisco"],
  ["Ferrari", 705, "Shell, IBM, HP"], ["Aston Martin", 615, "Aramco, TikTok, Cognizant"],
  ["Red Bull Racing", 399, "AT&T, Siemens, Oracle"], ["Alpine", 369, "Eni, Boeing, Claro"],
  ["Racing Bulls", 172, "Siemens, Randstad, Cash App"], ["Williams", 131, "Barclays, Komatsu, BNY"],
  ["Cadillac", 82, "Claro, Tenneco, Tommy Hilfiger"], ["Audi", 77, "Adidas, Visit Qatar, Hyatt Hotels"],
  ["Haas", 39, "MGM Resorts, CommScope, UChicago Medicine"],
];
const CAPTEAMS = ["Mercedes", "McLaren", "Ferrari", "Aston Martin", "Red Bull", "Alpine", "Racing Bulls", "Williams", "Cadillac", "Haas"];
const CAPROWS = [
  ["Partners (total)", "28", "54", "40", "34", "32", "42", "24", "27", "10", "22"],
  ["Public / private", "72 / 28%", "58 / 42%", "50 / 50%", "32 / 68%", "38 / 62%", "26 / 74%", "33 / 67%", "33 / 67%", "50 / 50%", "18 / 78%"],
  ["Tier 1 · mega-cap", "5", "6", "3", "3", "3", "1", "2", "2", "–", "–"],
  ["Tier 2 · large-cap", "9", "10", "5", "2", "2", "3", "1", "3", "1", "–"],
  ["Tier 3 · mid-cap", "6", "19", "9", "12", "10", "7", "9", "9", "7", "4"],
  ["Tier 4 · small-cap", "3", "18", "22", "16", "17", "31", "10", "13", "2", "17"],
];
const SECTOR = {
  teams: ["McLaren", "Aston Martin", "Alpine", "Williams", "Ferrari", "Red Bull", "Mercedes", "Racing Bulls", "Haas", "Audi", "Cadillac"],
  series: [
    ["Financial services & insurance", [6, 4, 4, 6, 5, 4, 3, 2, 2, 3, 1]],
    ["IT & internet", [17, 9, 4, 7, 6, 7, 12, 8, 6, 5, 2]],
    ["Consumer goods & retail", [8, 11, 13, 8, 9, 10, 4, 7, 6, 5, 2]],
    ["Energy", [2, 2, 2, 0, 1, 0, 0, 0, 0, 0, 0]],
    ["Life sciences", [0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0]],
  ],
};
// Fans working in the financial sector: index vs general population (100) and fanbase size
const FIN_FANS = [
  ["Mercedes", 172.9, 1375512], ["Audi", 168.0, 292833], ["Racing Bulls", 166.1, 137750], ["Aston Martin", 161.8, 701223],
  ["Red Bull", 160.8, 1494192], ["11-team average", 145.0, 756788], ["Alpine", 140.1, 262717], ["McLaren", 139.3, 1156740],
  ["Ferrari", 136.2, 1796424], ["Williams", 122.9, 298852], ["Cadillac", 115.2, 680210], ["Haas", 111.7, 128211],
];
// Kantar BrandZ 2026 Top 100: ranks the team marked as involved in F1
const KANTAR_GROUPS = [[1, 7], [9, 13], [16, 18], [24, 28], [32, 35], [39, 40], [44, 46],
  [52, 52], [56, 56], [60, 60], [69, 70], [72, 73], [82, 82], [84, 84], [91, 92]];

// ------------------------------------------------------------------ data (routes)
const MAX_BUSINESS = [ // business, Adyen products, what it does, can Adyen run it, verdict
  ["Verstappen.com online store", "Online Payments, Payment Methods", "Merchandise",
    "No, not without Fanatics. Fanatics runs the store under an exclusive deal and controls checkout.", "no"],
  ["Verstappen Travel: Orange Army grandstands (Austria, Spa, Hungary)", "Online Booking, Online Payments", "Ticket sales",
    "Yes, the most direct fit. Needs Verstappen.com's ticketing provider to connect to Adyen.", "yes"],
  ["Verstappen Travel: trailers (Austria, Spa, Hungary)", "Tap to Pay", "Trackside merchandise",
    "Yes, the most direct fit. Needs Verstappen.com's payment provider to connect to Adyen.", "yes"],
  ["Verstappen Racing (GT3)", "", "Potential trackside merchandise", "Possible.", "maybe"],
  ["Verstappen Racing (esports)", "", "Weekly Twitch streams; competition races", "Possible: \"Powered by Adyen\".", "maybe"],
  ["Verstappen Racing Pro Simulation (driver development)", "", "AI subscription-based driver development programme, in the works",
    "Possible. No payments today, so a new build.", "maybe"],
  ["Verstappen News", "", "Database", "Possible. No payments today, so a new build.", "maybe"],
  ["Verstappen official app (free: news, stats, alerts, shop link)", "", "Adds one-tap purchase of merchandise, grandstand tickets and experiences",
    "Possible. The app has no payments today, so a new build.", "maybe"],
];
const ALPINE_BUSINESS = [ // Alpine's business, activation, what Adyen does, outcome
  ["Team ecommerce store (new platform)", "The Integrated Commerce Garage",
    "Powers agreed parts of the Team's ecommerce environment: a dependable, locally relevant purchase journey for fans",
    "Measurable proof: checkout completion, payment performance, efficiency, customer experience"],
  ["Fan rewards", "Checkout to Chequered Flag Rewards",
    "Eligible online purchases unlock selected Team rewards, merchandise or experiences",
    "Engagement, conversion and repeat purchase"],
  ["Content and storytelling", "The Performance Proof Series",
    "Documentary films, technical features and executive interviews on the integration, plus short-form assets",
    "Flagship case study and sales enablement"],
  ["Enstone factory (UK)", "Commerce Under Pressure Live Lab",
    "Immersive session for customers and prospects: commerce scenarios, Team insights, expert discussion",
    "Credibility with customers and prospects"],
  ["Grand Prix host city, with an Adyen customer", "Race Week, One Platform",
    "A flagship venue becomes a race-week experience: booking, mobile ordering, venue payments, merchandise",
    "Live product demo and a three-party case study"],
  ["Grand Prix hospitality", "Adyen Commerce Club",
    "C-level programme at selected Grands Prix: hospitality, private discussions, garage tours, Team appearances",
    "Stronger relationships with priority accounts"],
  ["Team partner network", "One Platform Partner Forum",
    "Recurring forum connecting Team partners with Adyen experts, customers and enterprise leaders",
    "Qualified introductions and new business"],
];

const ROUTE_NAMES = ["Max Verstappen", "Alpine F1 Team", "Scuderia Ferrari"];

// ------------------------------------------------------------------ slides
async function build() {
  await defineLayouts();

  // ================================================================ Introduction
  pres.addSection({ title: "Introduction" });
  // Cover
  {
    const s = pres.addSlide({ masterName: "COVER", sectionTitle: "Introduction" });
    await photo(s, "adyen_kerb.jpg", 7.0, 0, W - 7.0, H, "Race track kerb");
    s.addText("PARTNERSHIP PROPOSAL", { placeholder: "eyebrow" });
    s.addText([{ text: "Adyen ×", options: { breakLine: true } }, { text: "Formula 1", options: { color: C.accent1 } }], { placeholder: "title" });
    s.addText("Why F1 is the right platform for Adyen, and how to win in it", { placeholder: "subtitle" });
    s.addText([{ text: "Prepared for " }, { text: "[ADD: name, Chairman]", options: { italic: true } }, { text: "  ·  " },
      { text: "[ADD: date]", options: { italic: true } }], { placeholder: "meta" });
    s.addNotes("Cover. Replace the [ADD] fields with the chairman's name and meeting date. Photo: Adyen 'Racing | Unified Payments' deck.");
  }

  // Adyen's brief (team deck slide 2)
  {
    const s = pres.addSlide({ masterName: "STATEMENT", sectionTitle: "Introduction" });
    await photo(s, "earth.jpg", 0, 0, W, H, "Earth from orbit");
    s.addShape(S.RECTANGLE, { x: 0, y: 0, w: W, h: H, fill: { color: C.text1, transparency: 30 }, line: { color: C.text1, width: 0 } });
    s.addText("ADYEN'S BRIEF", { placeholder: "eyebrow" });
    s.addText(t("Adyen: creating **financial efficiencies** in F1"), { placeholder: "title" });
    s.addText("ADYEN'S BRIEF DEFINES FOUR PRIORITIES FOR F1", { x: L, y: 2.75, w: 11, h: 0.3, fontSize: 12, bold: true,
      color: C.accent4, charSpacing: 1.5, margin: 0, isTextBox: true });
    const pr = [
      ["FiGlobe", "Global brand", "Show how Adyen's payments can power the financial business of F1"],
      ["FiUsers", "Client relationships", "Host partners, merchants and senior decision makers"],
      ["FiTrendingUp", "Commercial growth", "Win new deals, renew contracts and build pipeline"],
      ["FiFlag", "One global programme", "Unite local hosting across an initial 8–10 F1 races"],
    ];
    const cw = (CW - 0.9) / 4;
    for (const [i, [ic, head, body]] of pr.entries()) {
      const x = L + i * (cw + 0.3), y = 3.25;
      card(s, x, y, cw, 2.55, C.accent5, "Priority card");
      await iconDot(s, ic, x + 0.3, y + 0.3, 0.55);
      s.addText(head, { x: x + 0.3, y: y + 0.98, w: cw - 0.6, h: 0.62, fontSize: 16, bold: true, color: C.background1, margin: 0,
        isTextBox: true, valign: "bottom" });
      s.addText(body, { x: x + 0.3, y: y + 1.68, w: cw - 0.6, h: 0.8, fontSize: 13, color: C.accent4, margin: 0, isTextBox: true,
        valign: "top" });
    }
    s.addNotes("Source: Briefing - Adyen x Premium Experiences (Adyen), sections 1–5 and 7.\nAdyen wants a global brand and hospitality proposition that shows how payments power its partners, strengthens relationships with partners and merchants, and supports new deals, renewals and pipeline. The initial target is 8–10 races. The audience includes senior and C-suite decision makers. Budget, race selection, guest tiers, delivery scope and specific KPIs remain to be confirmed by Adyen.");
  }

  // Partnership hypothesis (team deck slide 3)
  {
    const s = pres.addSlide({ masterName: "STATEMENT", sectionTitle: "Introduction" });
    await photo(s, "f1_car_blur.jpg", 0, 0, W, H, "F1 car at speed");
    s.addShape(S.RECTANGLE, { x: 0, y: 0, w: W, h: H, fill: { color: C.text1, transparency: 40 }, line: { color: C.text1, width: 0 } });
    s.addText("OUR PARTNERSHIP HYPOTHESIS", { placeholder: "eyebrow" });
    s.addText(t("An F1 partnership can build Adyen's global brand and deepen client relationships through **payments storytelling** and a **global hospitality programme**"),
      { placeholder: "title" });
    s.addNotes("The one sentence the rest of the deck tests: section 1 (why F1), 2 (the business network), 3 (competition), 4 (proof), then the routes and our recommendation.");
  }

  // Executive summary
  {
    const s = content("CONTENT", "Introduction", "Executive summary",
      t("F1 gives Adyen a **global, enterprise-grade stage**, and payments is now one of its most contested categories"),
      "Source: GWI; GlobalData; F1; Adyen; Kantar; rights-holder proposals; SPORTFIVE analysis. See Sources and notes.",
      "Left: why F1 in four proof points. Right: the three routes in front of the chairman. Alpine and Max are filled from their proposals; Ferrari's proposal is still to come.");
    const rows = [
      ["625M", "A platform in growth", "F1 followers in 2026, up 30.8% since 2022. New sponsorship deal value is up 165% since 2020."],
      ["#1", "The audience Adyen sells to", "F1 ranks #1 of five major sports on all five Adyen audiences, from senior decision-makers to early tech adopters."],
      ["457M", "Where Adyen does business", "F1 fans across Adyen's 22 office markets, 13 of which host a 2027 race."],
      ["4", "A contested category", "Stripe, Airwallex, Mastercard and Visa already partner F1 teams. Adyen is not yet in F1."],
    ];
    const y0 = 2.0, rh = 1.1;
    rows.forEach(([big, head, body], i) => {
      const y = y0 + i * rh;
      if (i) s.addShape(S.LINE, { x: L, y: y - 0.06, w: 6.9, h: 0, line: { color: C.accent4, width: 0.75 } });
      s.addText(big, { x: L, y: y + 0.05, w: 1.75, h: 0.75, fontSize: 34, color: C.text1, margin: 0, valign: "top", isTextBox: true });
      s.addText([{ text: head, options: { bold: true, color: C.text1, breakLine: true } }, { text: body, options: { color: C.text2 } }],
        { x: L + 1.85, y: y + 0.05, w: 5.05, h: 0.95, fontSize: 13, margin: 0, valign: "top", paraSpaceAfter: 2, isTextBox: true });
    });
    const x = 7.85, w = R - x, y = 2.0, h = 4.6;
    card(s, x, y, w, h, C.text1, "Routes card");
    label(s, "Three routes into F1", x + 0.35, y + 0.28, w - 0.7, C.accent1);
    const routes = [
      ["Route 1 · Driver", "Max Verstappen", "Adyen powers the Verstappen ecosystem; Verstappen Travel ticketing is the most direct fit. 2027–2030."],
      ["Route 2 · Team", "Alpine F1 Team", "Exclusive Financial Technology Platform Partner; Adyen powers the Team's new ecommerce. £10.0M in 2027."],
      ["Route 3 · Team", "Scuderia Ferrari", null],
    ];
    routes.forEach(([kind, name, body], i) => {
      const ry = y + 0.68 + i * 1.07;
      if (i) s.addShape(S.LINE, { x: x + 0.35, y: ry - 0.08, w: w - 0.7, h: 0, line: { color: C.accent5, width: 0.75 } });
      s.addText([{ text: kind.toUpperCase() + "   ", options: { color: C.accent3, fontSize: 9.5, bold: true, charSpacing: 1 } },
        { text: name, options: { color: C.background1, fontSize: 14, bold: true, breakLine: true } },
        ...(body ? [{ text: body, options: { color: C.accent4, fontSize: 11 } }]
          : [{ text: "[ADD] ", options: { bold: true, color: C.accent1, fontSize: 11 } },
            { text: "Proposal to follow", options: { italic: true, color: C.accent4, fontSize: 11 } }])],
      { x: x + 0.35, y: ry, w: w - 0.7, h: 0.95, margin: 0, valign: "top", isTextBox: true });
    });
    label(s, "Decision needed", x + 0.35, y + 3.88, w - 0.7, C.accent1);
    s.addText(add("The approval you are asking the Chairman for", 11).map((r, i) => i ? { ...r, options: { ...r.options, color: C.accent4 } } : { ...r, options: { ...r.options, color: C.accent1 } }),
      { x: x + 0.35, y: y + 4.13, w: w - 0.7, h: 0.32, margin: 0, isTextBox: true, valign: "top" });
  }

  // ================================================================ 01 Why F1
  pres.addSection({ title: SECTIONS[0] });
  await divider(1, "Why Formula 1", "Growth, audience, footprint and brand value: what the data says about F1 as a platform for Adyen",
    "adyen_stadium.jpg", "Section 1 answers 'why F1 at all?' before any asset is discussed.");

  // Growth
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

  // Audience fit
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why Formula 1 · Audience",
      t("F1 is the strongest sport for **every audience Adyen sells to**"),
      "Source: GWI. Affinity index; ranking covers the five sports assessed. Benchmark per GWI methodology.",
      "Indices are not percentages. Definitions: high income = highest income segment; owners/founders = own or founded a business; senior decision-makers = influence over workplace purchasing; large company employees = companies with 1,001-5,000 employees; early tech adopters = among the first to adopt new technologies.\nNext-best sport: tennis on four measures, cycling on early tech adopters.");
    const cols = ["High income", "Owners / founders", "Senior decision-makers", "Large-company employees", "Early tech adopters"];
    const meaning = ["Premium consumers", "Merchant owners", "Enterprise buyers", "Enterprise accounts", "New-payment adopters"];
    const rows = [
      [hc("Sport"), ...cols.map((c) => hc(c, { align: "center" }))],
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

  // Footprint
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

  // Priority markets
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

  // Most valuable brands (team deck slide 38)
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why Formula 1 · Brand company",
      t("The world's most valuable brands **already invest in F1**"),
      "Source: Kantar BrandZ 2026 Most Valuable Global Brands (incl. data from S&P Capital IQ and Euromonitor). F1 involvement marked by SPORTFIVE.",
      "Kantar BrandZ 2026 Top 100. Boxes mark the brands the SPORTFIVE team identified as involved in F1 (40 of the 100 as marked). Check the marked set before quoting a count in the room.");
    const box = await fit(s, "kantar_list.png", L, 1.85, 5.6, 5.0, "Kantar BrandZ 2026 Top 100 list");
    const top = 25 / 1100, pitch = 18.714 / 1100, rowH = pitch;
    for (const [a, b] of KANTAR_GROUPS) {
      const right = a > 50;
      const ra = right ? a - 50 : a, rb = right ? b - 50 : b;
      const fx = right ? 0.495 : 0.03, fw = right ? 0.44 : 0.43;
      const y0 = box.y + box.h * (top + (ra - 1) * pitch - rowH * 0.52);
      const y1 = box.y + box.h * (top + (rb - 1) * pitch + rowH * 0.52);
      s.addShape(S.RECTANGLE, { x: box.x + box.w * fx, y: y0, w: box.w * fw, h: y1 - y0, fill: { color: C.accent1, transparency: 88 },
        line: { color: C.accent1, width: 1.25 }, objectName: "F1 brand highlight" });
    }
    const x = 6.75, w = R - x;
    s.addShape(S.RECTANGLE, { x, y: 2.02, w: 0.32, h: 0.2, fill: { color: C.accent1, transparency: 88 }, line: { color: C.accent1, width: 1.25 } });
    s.addText("Brand involved in F1 (SPORTFIVE analysis)", { x: x + 0.45, y: 1.97, w: w - 0.45, h: 0.3, fontSize: 11, color: C.text2,
      margin: 0, isTextBox: true, valign: "middle" });
    const pts = [
      ["FiCpu", "Enterprise tech sells through F1", "Google, Microsoft, Amazon, Oracle, IBM and Dell all use F1 to reach enterprise buyers."],
      ["FiCreditCard", "Payments is already on the grid", "Visa, Mastercard, American Express and Stripe sit in the Top 100 and in F1."],
      ["FiAward", "The room Adyen wants to be in", "F1 puts Adyen alongside the brands that set the benchmark for brand value."],
    ];
    for (const [i, [ic, head, body]] of pts.entries()) {
      const y = 2.6 + i * 1.3;
      await iconDot(s, ic, x, y, 0.5);
      s.addText([{ text: head, options: { bold: true, color: C.text1, breakLine: true } }, { text: body, options: { color: C.text2 } }],
        { x: x + 0.72, y: y - 0.03, w: w - 0.72, h: 1.1, fontSize: 13, margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 3 });
    }
    card(s, x, 6.05, w, 0.7, C.accent6, "So what");
    s.addText([{ text: "So what  ", options: { bold: true, color: C.accent2 } },
      { text: "F1 is where the world's most valuable brands build theirs.", options: { color: C.text1 } }],
    { x: x + 0.25, y: 6.05, w: w - 0.5, h: 0.7, fontSize: 13, margin: 0, valign: "middle", isTextBox: true });
  }

  // Brand value (team deck slide 39)
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why Formula 1 · Brand value",
      t("Strong brands **outperform the market**, and F1 partners are growing theirs"),
      "Source: Kantar × Google 2026 (European companies); Kantar BrandZ 2026 (Strong Brands Portfolio 2006–2026; IBM and American Express brand spotlights).",
      "Different, meaningful, salient: Kantar's drivers of brand equity. The IBM and American Express point is the team's analysis of Kantar BrandZ data: both posted their biggest brand-value increase in the year they entered F1 partnerships. Confirm before quoting.");
    const x1 = L, w1 = 4.75;
    card(s, x1, 2.0, w1, 4.0);
    label(s, "Portfolio performance index (2019 = 100)", x1 + 0.3, 2.2, w1 - 0.6);
    s.addChart(pres.charts.BAR, [
      { name: "2019", labels: ["Weak future power", "Stock market", "Strong future power"], values: [100, 100, 100] },
      { name: "2025", labels: ["Weak future power", "Stock market", "Strong future power"], values: [144, 172, 265] },
    ], { x: x1 + 0.1, y: 2.5, w: w1 - 0.2, h: 2.75, barDir: "col", ...chartBase(), chartColors: [HEX.context, HEX.green],
      showLegend: true, legendPos: "t", legendFontSize: 10, legendFontFace: "+mn-lt", legendColor: HEX.slate, valAxisMinVal: 0,
      dataLabelFontSize: 10, catAxisLabelFontSize: 10, barGapWidthPct: 60 });
    s.addText("Brands with the strongest future power returned 2.3x the STOXX Europe 600.", { x: x1 + 0.3, y: 5.3, w: w1 - 0.6, h: 0.55,
      fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top" });

    const x2 = x1 + w1 + 0.3, w2 = 3.3;
    card(s, x2, 2.0, w2, 4.0, C.text1, "Return card");
    label(s, "Total return, 2006–2026", x2 + 0.3, 2.2, w2 - 0.6, C.accent1);
    const ret = [["504%", "Kantar Strong Brands Portfolio", true], ["451%", "S&P 500", false], ["234%", "MSCI World Index", false]];
    ret.forEach(([big, lab, on], i) => {
      const y = 2.6 + i * 1.08;
      s.addText(big, { x: x2 + 0.3, y, w: w2 - 0.6, h: 0.55, fontSize: on ? 34 : 26, bold: on, color: on ? C.accent1 : C.background1,
        margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: x2 + 0.3, y: y + 0.55, w: w2 - 0.6, h: 0.3, fontSize: 11.5, color: C.accent4, margin: 0, isTextBox: true });
    });

    const x3 = x2 + w2 + 0.3, w3 = R - x3;
    const brands = [["IBM", "$150.8B", "2026 brand value, +20% vs 2025", "Ferrari partner"],
      ["American Express", "$80.3B", "2026 brand value, +22% vs 2025; doubled since 2024", "Official F1 partner"]];
    brands.forEach(([name, big, body, tag], i) => {
      const y = 2.0 + i * 2.05, h = 1.9;
      card(s, x3, y, w3, h);
      s.addText(name, { x: x3 + 0.3, y: y + 0.2, w: w3 - 0.6, h: 0.32, fontSize: 13, bold: true, color: C.text1, margin: 0, isTextBox: true });
      s.addText(big, { x: x3 + 0.3, y: y + 0.55, w: w3 - 0.6, h: 0.55, fontSize: 28, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText([{ text: body, options: { color: C.text2, breakLine: true } }, { text: tag, options: { color: C.accent2, bold: true } }],
        { x: x3 + 0.3, y: y + 1.1, w: w3 - 0.6, h: 0.7, fontSize: 11, margin: 0, isTextBox: true, valign: "top" });
    });
    soWhat(s, "IBM and American Express both posted their **biggest brand-value gains in the year they entered F1** partnerships.", 6.15);
  }

  // So what for Adyen
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

  // ================================================================ 02 F1 as a business network
  pres.addSection({ title: SECTIONS[1] });
  await divider(2, "F1 as a business network", "Who Adyen would sit alongside: each team's partner network by size, sector and audience",
    "adyen_office.jpg", "Section 2 is the partnership-selection lens from the team deck: networks and audience.");

  // Team partnership network (team deck slide 15)
  {
    const s = content("CONTENT", SECTIONS[1], "02 Business network · Partner revenue",
      t("Mercedes, McLaren and Ferrari bring the **largest partner networks**"),
      "Source: SPORTFIVE analysis. 2024–2025 public data; estimates where no disclosure; some revenues from parent-company segments. USD at 2024–25 average FX (Bloomberg/ECB).",
      "Partners' total combined revenue by team, and each team's three largest partners by reported annual revenue. Team note: figures being re-checked (GF). Alpine and Ferrari are highlighted as the two team routes.");
    label(s, "Partners' total combined revenue ($ billion)", L, 2.0, 6.2);
    const hi = (n) => n === "Alpine" || n === "Ferrari";
    s.addChart(pres.charts.BAR, [{ name: "Combined revenue ($B)", labels: NETWORK.map((r) => r[0]), values: NETWORK.map((r) => r[1]) }], {
      x: L - 0.1, y: 2.3, w: 6.3, h: 4.45, barDir: "bar", ...chartBase(), catAxisOrientation: "maxMin", barGapWidthPct: 40,
      chartColors: NETWORK.map((r) => (hi(r[0]) ? HEX.green : HEX.context)), dataLabelFormatCode: '"$"#,##0"B"',
      catAxisLabelFontSize: 10.5, dataLabelFontSize: 10.5, valAxisMinVal: 0, valAxisMaxVal: 1250,
    });
    const x = 6.95, w = R - x;
    const rows = [[hc("Team"), hc("Top 3 partners by reported annual revenue")],
      ...NETWORK.map(([team, , top]) => [
        { text: team, options: { bold: true, color: C.text1, fontSize: 10.5, valign: "middle", fill: { color: hi(team) ? C.accent6 : C.background1 } } },
        { text: top, options: { color: C.text2, fontSize: 10.5, valign: "middle", fill: { color: hi(team) ? C.accent6 : C.background1 } } },
      ])];
    s.addTable(rows, { x, y: 2.0, w, colW: [1.75, w - 1.75], rowH: [0.38, ...NETWORK.map(() => 0.355)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.1, 0.03, 0.1], objectName: "Top partners table" });
  }

  // Market-cap segmentation (team deck slide 16)
  {
    const s = content("CONTENT", SECTIONS[1], "02 Business network · Partner profile",
      t("McLaren and Mercedes lead on blue-chip partners; **Alpine's 42 partners are mostly private**"),
      "Source: SPORTFIVE analysis. Public data; estimates where no disclosure. USD at 2024–25 average FX (Bloomberg/ECB). Audi not included.",
      "Market-cap tiers: Tier 1 mega-cap $200B+; Tier 2 large-cap $50–200B; Tier 3 mid-cap $5–50B; Tier 4 small-cap below $5B. Team note: figures being re-checked (GF). Haas public/private split as supplied (18/78) does not sum to 100: check.");
    const tiers = [["Tier 1", "Mega-cap", "$200B+"], ["Tier 2", "Large-cap", "$50–200B"], ["Tier 3", "Mid-cap", "$5–50B"], ["Tier 4", "Small-cap", "below $5B"]];
    tiers.forEach(([tier, name, range], i) => {
      const x = L + i * 3.07;
      s.addText([{ text: tier + "  ", options: { bold: true, color: C.text1 } }, { text: name + " · " + range, options: { color: C.text2 } }],
        { x, y: 2.0, w: 2.95, h: 0.3, fontSize: 11, margin: 0, isTextBox: true, valign: "middle" });
    });
    const hiCol = (j) => CAPTEAMS[j] === "Alpine" || CAPTEAMS[j] === "Ferrari";
    const rows = [[hc(""), ...CAPTEAMS.map((tm, j) => hc(tm, { align: "center", fontSize: 10.5, fill: { color: hiCol(j) ? C.accent2 : C.text1 } }))],
      ...CAPROWS.map(([lab, ...vals], i) => [
        { text: lab, options: { bold: true, color: C.text1, fontSize: 11, valign: "middle", fill: { color: C.background2 } } },
        ...vals.map((v, j) => ({ text: v, options: { color: C.text1, bold: i === 0, fontSize: i === 1 ? 10.5 : 12, align: "center", valign: "middle",
          fill: { color: hiCol(j) ? C.accent6 : C.background1 } } })),
      ])];
    s.addTable(rows, { x: L, y: 2.5, w: CW, colW: [2.03, ...CAPTEAMS.map(() => 1.01)], rowH: [0.5, ...CAPROWS.map(() => 0.52)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.06, 0.03, 0.06], objectName: "Market cap table" });
    soWhat(s, "McLaren (6) and Mercedes (5) have the most **mega-cap partners**; 31 of Alpine's 42 partners are small-cap and 74% are private.", 6.25);
  }

  // Partner mapping by sector (team deck slide 17)
  {
    const s = content("CONTENT", SECTIONS[1], "02 Business network · Sector mapping",
      t("Financial services already sits in **every team's partner network**"),
      "Source: SPORTFIVE partner mapping. Relevant team partners only, by sector.",
      "Number of relevant team partners by sector. FS&I = financial services and insurance; IT&I = IT and internet. Team note: figures being re-checked (GF).");
    s.addChart(pres.charts.BAR, SECTOR.series.map(([name, vals]) => ({ name, labels: SECTOR.teams, values: vals.map((v) => v || null) })), {
      x: L - 0.1, y: 1.95, w: CW + 0.2, h: 4.15, barDir: "col", barGrouping: "stacked", ...chartBase(),
      chartColors: [HEX.green, HEX.navy, HEX.g1, HEX.g2, HEX.g3], showValue: true, dataLabelPosition: "ctr", dataLabelColor: "FFFFFF",
      dataLabelFontSize: 10, dataLabelFontBold: true, showLegend: true, legendPos: "t", legendFontSize: 10.5, legendFontFace: "+mn-lt",
      legendColor: HEX.slate, barGapWidthPct: 45, catAxisLabelFontSize: 10.5,
    });
    soWhat(s, "every team counts financial-services partners, from 1 (Cadillac) to 6 (McLaren, Williams). **Alpine has 4, Ferrari 5.**", 6.2);
  }

  // Fans working in financial sector (team deck slide 20)
  {
    const s = content("CONTENT", SECTIONS[1], "02 Business network · Fans in finance",
      t("Every team's fans over-index on **working in financial services**"),
      "Source: Global Web Index (2026). Index vs general population (= 100). North America and Europe (excl. Russia). Average of 11 teams.",
      "Index and size of each team's fanbase working in the financial sector. Highest index: Mercedes (172.9). Largest pool: Ferrari (1.80M). Alpine: 140.1, 0.26M.");
    label(s, "Index vs general population (= 100) · fans in financial services", L, 2.0, 7.6);
    const colorOf = (n) => (n === "Alpine" || n === "Ferrari" ? HEX.green : n.startsWith("11") ? HEX.navy : HEX.context);
    s.addChart(pres.charts.BAR, [{ name: "Index", labels: FIN_FANS.map(([n, , sz]) => `${n}  (${(sz / 1e6).toFixed(2)}M)`), values: FIN_FANS.map((r) => r[1]) }], {
      x: L - 0.1, y: 2.3, w: 7.8, h: 4.45, barDir: "bar", ...chartBase(), catAxisOrientation: "maxMin", barGapWidthPct: 40,
      chartColors: FIN_FANS.map((r) => colorOf(r[0])), dataLabelFormatCode: "0.0", catAxisLabelFontSize: 10.5, dataLabelFontSize: 10.5,
      valAxisMinVal: 0, valAxisMaxVal: 200,
    });
    const stats = [["172.9", "Mercedes fans", "The highest index of any team"], ["1.80M", "Ferrari fans", "The largest pool working in financial services"],
      ["140.1", "Alpine fans", "0.26M fans in financial services"]];
    stats.forEach(([big, head, body], i) => {
      const x = 8.75, w = R - x, y = 2.0 + i * 1.6, h = 1.45;
      card(s, x, y, w, h);
      s.addText(big, { x: x + 0.3, y: y + 0.15, w: w - 0.6, h: 0.55, fontSize: 28, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText([{ text: head, options: { bold: true, color: C.text1, breakLine: true } }, { text: body, options: { color: C.text2 } }],
        { x: x + 0.3, y: y + 0.7, w: w - 0.6, h: 0.65, fontSize: 11.5, margin: 0, isTextBox: true, valign: "top" });
    });
  }

  // ================================================================ 03 Competitive landscape
  pres.addSection({ title: SECTIONS[2] });
  await divider(3, "Competitive landscape", "Who is already using sport, and F1 in particular, to win in payments",
    "adyen_paylink.jpg", "Section 3 shows the category is moving: competitors are in, and the benchmark has shifted from logos to integration.");

  // Payments in F1
  {
    const s = content("CONTENT", SECTIONS[2], "03 Competitive landscape · Payments in F1",
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
    s.addText([{ text: "Not yet in F1.  ", options: { bold: true, color: C.text1 } },
      { text: "Three routes are on the table: Max Verstappen, Alpine and Ferrari.", options: { color: C.text1 } }],
    { x: gx + 1.3, y: ay, w: R - gx - 1.55, h: 0.82, fontSize: 13, margin: 0, valign: "middle", isTextBox: true });
  }

  // Competitors across sport
  {
    const s = content("CONTENT", SECTIONS[2], "03 Competitive landscape · Competitors in sport",
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

  // Airwallex x McLaren benchmark
  {
    const s = content("CONTENT", SECTIONS[2], "03 Competitive landscape · The benchmark",
      t("The model to beat: Airwallex × McLaren, **integration not a logo**"),
      "Source: SPORTFIVE analysis; McLaren Racing and Airwallex case study.",
      "The benchmark Adyen's brief sets: a payments brand inside the team's business. Section 4 shows the detail, including SPORTFIVE's role in the deal.");
    await photo(s, "airwallex_carbon.jpg", L, 2.0, 4.55, 4.6, "Airwallex branding on McLaren carbon fibre");
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
    s.addText([{ text: "Reported results  ", options: { bold: true, color: C.text1 } },
      { text: "live in 14 days; 90% of McLaren's payments arrive within hours, 65% instantly; local payment networks in 110+ countries.",
        options: { color: C.text2 } }], { x, y: 4.22, w, h: 0.55, fontSize: 12, margin: 0, isTextBox: true, valign: "top" });
    card(s, x, 4.9, w, 1.7, C.accent6, "Lessons");
    label(s, "What it means for Adyen", x + 0.3, 5.05, w - 0.6, C.accent2);
    s.addText([
      { text: "Lead with where Adyen sits inside the partner's business, not the logo.", options: { bullet: true, breakLine: true } },
      { text: "Show a clear line to revenue and payment volume.", options: { bullet: true, breakLine: true } },
      { text: "Put hospitality at the centre, connecting people across the partner's ecosystem.", options: { bullet: true } },
    ], { x: x + 0.3, y: 5.35, w: w - 0.6, h: 1.15, fontSize: 13, color: C.text1, margin: 0, valign: "top", paraSpaceAfter: 4, isTextBox: true });
  }

  // ================================================================ 04 Proof and credentials
  pres.addSection({ title: SECTIONS[3] });
  await divider(4, "Proof and credentials", "What F1 partners get back, and what SPORTFIVE has already delivered in payments",
    "adyen_analytics.jpg", "Section 4: proof of concept and delivery credentials.");

  // F1 team case studies (team deck slides 22-23)
  {
    const s = content("CONTENT", SECTIONS[3], "04 Proof · F1 partner case studies",
      t("F1 partners report **real commercial returns** from hosting at races"),
      "Source: Komatsu × Williams, HPE × Mercedes and Businessolver × Alpine published case material, as compiled by SPORTFIVE.",
      "Three partners, three proof points: deals closed at races (Komatsu), revenue opportunity accelerated (HPE) and pipeline influenced (Businessolver, an Alpine partner).");
    const cw = (CW - 0.6) / 3, y = 2.0, h = 4.75;
    const cases = [
      { pair: "Komatsu × Williams", big: "$100M+", lab: "orders received at races",
        body: "Komatsu hosts key global stakeholders at races, many at a Komatsu event for the first time: a unique setting for client relationships and deal acceleration.",
        stats: [["3,735", "stakeholders hosted"], ["90%", "found it useful for business discussions"], ["94%", "guest satisfaction"]] },
      { pair: "HPE × Mercedes", big: "$300M+", lab: "revenue opportunity accelerated from race activations alone",
        quote: "\"For us, the real value has been the ability to authentically showcase our technology through Mercedes F1 use cases in advertising, on digital platforms, at strategic events, with press and analysts, and through direct customer engagement at races.\"",
        by: "Antonio Neri, CEO, Hewlett Packard Enterprise" },
      { pair: "Businessolver × Alpine", big: "$122M", lab: "business pipeline influenced by at-track hosting and experiences",
        body: "Technology powered by people: Businessolver uses its Alpine partnership to bring clients into F1 and showcase AI, decision-support and real-time analytics.",
        tag: "An Alpine partner (Route 2)" },
    ];
    cases.forEach((c, i) => {
      const x = L + i * (cw + 0.3);
      card(s, x, y, cw, h, i === 1 ? C.text1 : C.background2);
      const dark = i === 1;
      s.addText(c.pair.toUpperCase(), { x: x + 0.3, y: y + 0.25, w: cw - 0.6, h: 0.3, fontSize: 11, bold: true, charSpacing: 1,
        color: dark ? C.accent1 : C.accent2, margin: 0, isTextBox: true });
      s.addText(c.big, { x: x + 0.3, y: y + 0.6, w: cw - 0.6, h: 0.75, fontSize: 40, bold: true, color: dark ? C.accent1 : C.text1,
        margin: 0, isTextBox: true, valign: "top" });
      s.addText(c.lab, { x: x + 0.3, y: y + 1.38, w: cw - 0.6, h: 0.55, fontSize: 12.5, bold: true, color: dark ? C.background1 : C.text1,
        margin: 0, isTextBox: true, valign: "top" });
      if (c.body) s.addText(c.body, { x: x + 0.3, y: y + 2.05, w: cw - 0.6, h: 1.2, fontSize: 11.5, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
      if (c.stats) c.stats.forEach(([b, l], k) => {
        const sy = y + 3.3 + k * 0.45;
        s.addText([{ text: b + "  ", options: { bold: true, color: C.text1, fontSize: 14 } }, { text: l, options: { color: C.text2, fontSize: 11 } }],
          { x: x + 0.3, y: sy, w: cw - 0.6, h: 0.4, margin: 0, isTextBox: true, valign: "middle" });
      });
      if (c.quote) {
        s.addText(c.quote, { x: x + 0.3, y: y + 2.05, w: cw - 0.6, h: 1.95, fontSize: 11.5, italic: true, color: C.accent4, margin: 0, isTextBox: true, valign: "top" });
        s.addText(c.by, { x: x + 0.3, y: y + 4.1, w: cw - 0.6, h: 0.4, fontSize: 10.5, bold: true, color: C.background1, margin: 0, isTextBox: true });
      }
      if (c.tag) {
        s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.3, y: y + 3.55, w: cw - 0.6, h: 0.5, rectRadius: 0.08, fill: { color: C.accent6 },
          line: { color: C.accent1, width: 1 } });
        s.addText(c.tag, { x: x + 0.45, y: y + 3.55, w: cw - 0.9, h: 0.5, fontSize: 11, bold: true, color: C.accent2, margin: 0, isTextBox: true, valign: "middle" });
      }
    });
  }

  // SPORTFIVE credentials (team deck slide 24)
  {
    const s = content("CONTENT", SECTIONS[3], "04 Proof · SPORTFIVE credentials",
      t("This is what we've done: **Airwallex × McLaren**, powering performance"),
      "Source: SPORTFIVE. Images: McLaren Racing and Airwallex.",
      "SPORTFIVE's flagship F1 payments credential. We showcased Airwallex's payment solutions to enterprises worldwide through McLaren. Add: how Airwallex helped McLaren on speed (see next slide).");
    await fit(s, "mclaren_airwallex_logos.png", L, 1.95, 2.3, 1.3, "McLaren and Airwallex logos");
    s.addText("Showcased Airwallex's payment service solutions to a wide variety of enterprises on a global scale.",
      { x: L + 2.55, y: 2.0, w: 4.05, h: 1.2, fontSize: 15, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    const iw = (6.6 - 0.4) / 3;
    const imgs = [["airwallex_carbon.jpg", "Airwallex on McLaren carbon fibre"], ["airwallex_drivers.jpg", "McLaren drivers, Airwallex partner content"],
      ["airwallex_install.jpg", "Airwallex installation with McLaren driver"]];
    for (const [i, [f, alt]] of imgs.entries()) await photo(s, f, L + i * (iw + 0.2), 3.55, iw, 3.05, alt);
    const x = 7.55, w = R - x;
    card(s, x, 1.95, w, 4.65, C.text1, "Scope card");
    label(s, "Our scope of advisory and execution", x + 0.35, 2.2, w - 0.7, C.accent1);
    const scope = ["Diagnosed the FinTech enterprise awareness gap", "Mapped the F1 B2B opportunity landscape",
      "Benchmarked fintech differentiation and positioning", "Built a B2B partnership evaluation model", "Modelled investment scenario trade-offs",
      "Engineered an enterprise-focused rights portfolio", "Structured the deal for network access", "Enabled a board-level partnership decision"];
    const check = await icon("FiCheck", "0ABF53");
    scope.forEach((it, i) => {
      const y = 2.65 + i * 0.48;
      s.addImage({ data: check, x: x + 0.35, y: y + 0.05, w: 0.24, h: 0.24 });
      s.addText(it, { x: x + 0.75, y, w: w - 1.1, h: 0.36, fontSize: 12.5, color: C.background1, margin: 0, isTextBox: true, valign: "middle" });
    });
  }

  // Proof of concept (team deck slide 25)
  {
    const s = content("CONTENT", SECTIONS[3], "04 Proof · Proof of concept",
      t("How Airwallex **optimised McLaren's financial operations**"),
      "Source: McLaren Racing modernises cross-border payments with Airwallex (Airwallex case study), as compiled by SPORTFIVE.",
      "McLaren Racing modernises cross-border payments with Airwallex. The point for Adyen: a payments partner that solves a real operational problem for the team earns the case study.");
    const lw = 5.55;
    label(s, "Business challenge", L, 2.0, lw);
    s.addText([
      { text: "McLaren Racing operates across 24 race locations, with frequent international supplier payments.", options: { bullet: true, breakLine: true } },
      { text: "A manual process: around 30 payments per run, high FX and transfer fees, 2–5 day settlement via banks and SWIFT.", options: { bullet: true, breakLine: true } },
      { text: "Under F1's cost cap, efficiency frees budget for on-track performance.", options: { bullet: true } },
    ], { x: L, y: 2.3, w: lw, h: 1.65, fontSize: 12, color: C.text1, margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 4 });
    label(s, "Airwallex solution", L, 4.05, lw);
    s.addText([
      { text: "Implemented in 14 days.", options: { bullet: true, breakLine: true } },
      { text: "Automated global payment workflows: batch payouts, approvals, faster cross-border transfers.", options: { bullet: true, breakLine: true } },
      { text: "Suppliers paid in local currencies; integrated with existing banking and accounting for cash-flow visibility.", options: { bullet: true } },
    ], { x: L, y: 4.35, w: lw, h: 1.65, fontSize: 12, color: C.text1, margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 4 });
    const x = 6.55, w = R - x, tw = (w - 0.3) / 2, th = 1.15;
    const tiles = [["14 days", "to implement"], ["0.5 day", "saved per month on payment runs"], ["£4,000+", "annual savings on transaction and FX fees"],
      ["110+", "countries with local payment networks"]];
    tiles.forEach(([big, lab], i) => {
      const tx = x + (i % 2) * (tw + 0.3), ty = 2.0 + Math.floor(i / 2) * (th + 0.2);
      card(s, tx, ty, tw, th);
      s.addText(big, { x: tx + 0.25, y: ty + 0.12, w: tw - 0.5, h: 0.5, fontSize: 24, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: tx + 0.25, y: ty + 0.65, w: tw - 0.5, h: 0.42, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    const by = 2.0 + 2 * (th + 0.2);
    card(s, x, by, w, 1.15, C.text1, "Speed tile");
    s.addText([{ text: "90%  ", options: { bold: true, color: C.accent1, fontSize: 24 } },
      { text: "of payments arrive within hours, ", options: { color: C.background1, fontSize: 12 } },
      { text: "65% ", options: { bold: true, color: C.accent1, fontSize: 14 } }, { text: "instantly", options: { color: C.background1, fontSize: 12 } }],
    { x: x + 0.25, y: by, w: w - 0.5, h: 1.15, margin: 0, isTextBox: true, valign: "middle" });
    soWhat(s, "lower payment costs, no manual runs and faster cash movement: **efficiencies McLaren reinvests in racing performance**.", 6.15);
  }

  // ================================================================ 05 The opportunities
  pres.addSection({ title: SECTIONS[4] });
  await divider(5, "The opportunities", "Three routes into F1: Max Verstappen, Alpine F1 Team and Scuderia Ferrari",
    "adyen_crowd.jpg", "Section 5. Each route uses the same three slides (overview, business opportunity, rights) so the chairman can compare like for like. Ferrari's proposal is still to come.");

  // Routes at a glance
  {
    const s = content("CONTENT", SECTIONS[4], "05 The opportunities · Overview",
      t("Three routes into F1 for Adyen"),
      "Source: Max Verstappen × Adyen rights package (for discussion); Alpine F1 Team Provisional Rights Overview 2027–2029; Ferrari to follow.",
      "One line per field. Detail slides follow in the same order. Max's fee and Ferrari's proposal still to add.");
    const cw = (CW - 0.6) / 3;
    const routes = [
      { n: 1, type: "Driver", name: "Max Verstappen", img: null, fields: [
        ["The opportunity", "Official ambassador; Adyen powers the Verstappen business ecosystem"],
        ["Where Adyen sits", "Verstappen Travel ticketing and trailers; Pro Simulation booking"],
        ["Investment", null], ["Term and status", "2027–2030, non-exclusive; for discussion"]] },
      { n: 2, type: "Team", name: "Alpine F1 Team", img: "alpine_engine.jpg", fields: [
        ["The opportunity", "Exclusive Financial Technology Platform Partner, global"],
        ["Where Adyen sits", "Powers the Team's new ecommerce platform, then hospitality and network"],
        ["Investment", "£10.0M in 2027, +5% a year (£31.5M over 3 years)"], ["Term and status", "2027–2029; provisional, subject to contract"]] },
      { n: 3, type: "Team", name: "Scuderia Ferrari", img: null, fields: [["The opportunity", null], ["Where Adyen sits", null],
        ["Investment", null], ["Term and status", null]] },
    ];
    for (const [i, r] of routes.entries()) {
      const x = L + i * (cw + 0.3), y = 2.0;
      card(s, x, y, cw, 4.75);
      if (r.img) await photo(s, r.img, x + 0.25, y + 0.25, cw - 0.5, 1.0, "Alpine car with Adyen branding (mock-up)");
      else ph(s, x + 0.25, y + 0.25, cw - 0.5, 1.0, r.n === 1 ? "Photo of Max Verstappen" : "Image or logo", { size: 11 });
      label(s, `Route ${r.n} · ${r.type}`, x + 0.3, y + 1.4, cw - 0.6, C.accent2);
      s.addText(r.name, { x: x + 0.3, y: y + 1.66, w: cw - 0.6, h: 0.42, fontSize: 19, bold: true, color: C.text1, margin: 0, isTextBox: true });
      r.fields.forEach(([f, v], k) => {
        const fy = y + 2.2 + k * 0.63;
        s.addText([{ text: f + "  ", options: { bold: true, color: C.text1, breakLine: true } },
          ...(v ? [{ text: v, options: { color: C.text2 } }] : add(r.n === 3 ? "proposal to follow" : "fee", 10.5))],
        { x: x + 0.3, y: fy, w: cw - 0.6, h: 0.56, fontSize: 10.5, margin: 0, isTextBox: true, valign: "top" });
      });
    }
  }

  // ---------- Route 1: Max Verstappen (team deck slides 28-30)
  {
    const s = content("CONTENT_PHOTO", SECTIONS[4], "05 The opportunities · Route 1 · Max Verstappen",
      t("Two Dutch innovators: **Adyen powers the Verstappen ecosystem**"),
      "Source: Max Verstappen × Adyen rights package (for discussion); followers as supplied.",
      "Adyen powers Max Verstappen. Add a photo of Max in the picture placeholder on the left. Follower counts as supplied in the team deck; check before the meeting.");
    const x = 5.35, w = R - x;
    s.addText("Max Verstappen has built one of the most successful personal brands in global sport; Adyen has built one of the world's leading financial technology platforms. Together they can create a living case study of how high-performance businesses are built, operated and scaled. Max is an athlete entrepreneur with businesses beyond F1, so Adyen becomes the technology platform behind the Verstappen ecosystem, powering customer journeys across racing, travel, merchandise and experiences. The commercial integration creates genuine proof of performance; the marketing rights tell that story to customers, prospects and partners worldwide.",
      { x, y: 1.95, w, h: 2.35, fontSize: 13.5, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    label(s, "Social reach", x, 4.4, w);
    const soc = [["19.3M", "Instagram followers"], ["3M", "Facebook"], ["1M", "YouTube"]];
    const tw = (w - 0.5) / 3;
    soc.forEach(([big, lab], i) => {
      const tx = x + i * (tw + 0.25);
      card(s, tx, 4.72, tw, 1.0);
      s.addText(big, { x: tx + 0.25, y: 4.8, w: tw - 0.5, h: 0.5, fontSize: 24, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: tx + 0.25, y: 5.3, w: tw - 0.5, h: 0.3, fontSize: 11, color: C.text2, margin: 0, isTextBox: true });
    });
    label(s, "Top markets by followers", x, 5.95, w);
    ["USA", "Brazil", "Netherlands", "Mexico", "UK", "Germany"].forEach((m, i) => {
      const cx = x + i * 1.2;
      s.addShape(S.ROUNDED_RECTANGLE, { x: cx, y: 6.25, w: 1.08, h: 0.36, rectRadius: 0.18, fill: { color: C.accent6 }, line: { color: C.accent6, width: 0 } });
      s.addText(m, { x: cx, y: 6.25, w: 1.08, h: 0.36, fontSize: 11, bold: true, color: C.accent2, align: "center", valign: "middle", margin: 0, isTextBox: true });
    });
  }
  {
    const s = content("CONTENT", SECTIONS[4], "05 The opportunities · Route 1 · Business opportunity",
      t("Max is a business ecosystem: **Verstappen Travel is the most direct fit** for Adyen"),
      "Source: SPORTFIVE assessment of the Verstappen business ecosystem.",
      "Powering a high-performance ecosystem. Blank Adyen-product cells are still to define with Adyen. The online store is out of reach while Fanatics holds the exclusive deal.");
    const vfill = { yes: C.accent6, no: C.background2, maybe: C.background1 };
    const rows = [[hc("Max's business"), hc("Adyen products"), hc("What it does"), hc("Can Adyen run it?")],
      ...MAX_BUSINESS.map(([biz, prod, what, can, v]) => [
        { text: biz, options: { bold: true, color: C.text1, fontSize: 10.5, valign: "middle" } },
        prod ? { text: prod, options: { color: C.text1, fontSize: 10.5, valign: "middle" } }
          : { text: "[ADD]", options: { italic: true, color: C.accent3, fontSize: 10.5, valign: "middle" } },
        { text: what, options: { color: C.text2, fontSize: 10.5, valign: "middle" } },
        { text: [{ text: can.split(/(?<=[.:,])\s/)[0] + " ", options: { bold: true, color: v === "yes" ? C.accent2 : C.text1 } },
          { text: can.split(/(?<=[.:,])\s/).slice(1).join(" "), options: { color: C.text2 } }],
          options: { fontSize: 10.5, valign: "middle", fill: { color: vfill[v] } } },
      ])];
    s.addTable(rows, { x: L, y: 2.0, w: CW, colW: [3.2, 2.2, 3.15, 3.58], rowH: [0.4, ...MAX_BUSINESS.map(() => 0.53)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.04, 0.1, 0.04, 0.1], objectName: "Max business table" });
  }
  {
    const s = content("CONTENT", SECTIONS[4], "05 The opportunities · Route 1 · Rights package",
      t("Rights package: **Max Verstappen × Adyen**"),
      "Source: Max Verstappen × Adyen rights package, for discussion purposes. Not a contract.",
      "Transcribed from the rights package in the team deck. The GT3 car position reads 'to discuss (not full car)'. Paddock Club hospitality is a SPORTFIVE addition: Max's own package excludes Red Bull assets and hospitality, so confirm how it is delivered.");
    s.addText([{ text: "A strong opportunity to support Adyen's entry into motorsport with four-time World Champion Max Verstappen and his personal racing pillars: GT3, Rally and Sim Racing. ", options: { color: C.text1 } },
      { text: "For discussion purposes.", options: { color: C.accent2, bold: true } }],
    { x: L, y: 1.9, w: CW, h: 0.5, fontSize: 12, margin: 0, isTextBox: true, valign: "top" });
    const cols = [
      [["h", "Duration: 2027–2030 (3 years)"], ["h", "Ambassador role"],
        ["b", "Max Verstappen as official ambassador"],
        ["b", "1 full day (6 hours) of driver time in a personal capacity, e.g. ad campaign, social content, press interviews"],
        ["b", "3 × 15-minute paddock meet-and-greets with Max, each for 3 VIP guests"],
        ["b", "Rights: non-exclusive. IP rights of Max in his personal and Verstappen Racing capacity only: digital and online, TV ad, print, out of home"]],
      [["h", "Hospitality"], ["b", "Formula 1 garage tour for 2 VIP guests"], ["b", "Private track day for stakeholders"],
        ["b", "SPORTFIVE addition: Paddock Club hospitality at selected Adyen races throughout the season (to confirm)"],
        ["h", "Adyen business integration"],
        ["kv", "Verstappen Travel B2C:", "official Orange Army grandstand ticketing for the Spa and Austria GPs 2027 (to discuss); branding on trailers and Orange Army goodie bags; joint B2C ticketing partnership in GTWC, e.g. 24 Hours of Spa (to discuss)"],
        ["kv", "Verstappen Pro Simulation:", "booking payment system"]],
      [["h", "Branding: GT3, Rally and Sim Racing"],
        ["kv", "Helmets:", "Max's private Verstappen Racing helmet (chin); helmets of all Verstappen Racing drivers (chin)"],
        ["kv", "Car and garage:", "Verstappen Racing Mercedes GT3 2027 car (position to discuss, not full car); garage branding (to discuss)"],
        ["kv", "Race wear:", "race suit and underwear top (front chest and sleeves); cool vest (front chest); gloves"],
        ["kv", "Team wear:", "multiple items (front chest)"],
        ["h", "Content"], ["b", "Max Verstappen and Verstappen.com social channels (to discuss)"]],
    ];
    rightsColumns(s, cols, 2.6, 4.2, [L, L + 4.15, L + 8.3], [3.85, 3.85, 3.83], 11);
  }

  // ---------- Route 2: Alpine (Alpine Provisional Rights Overview 2027-2029)
  {
    const s = content("CONTENT", SECTIONS[4], "05 The opportunities · Route 2 · Alpine F1 Team",
      t("Alpine: **Performance in Every Transaction**, from checkout to chequered flag"),
      "Source: Alpine Formula One Team, Provisional Rights Overview 2027–2029 (not legally binding). Audience: GWI Core, Q3 2025–Q2 2026, all internet users.",
      "Alpine's objectives for Adyen: (1) prove the enterprise platform through a measurable ecommerce integration and a client-facing case study; (2) deepen relationships with priority customers through C-level hospitality and F1 experiences; (3) generate qualified new business through the Team's international partner network. Apple Pay audience data covers selected markets only. Car image is Alpine's mock-up of Adyen branding.");
    const lw = 6.15;
    s.addText("Every F1 result depends on thousands of complex processes working together with speed, precision and resilience; Adyen does the same for enterprise commerce. As the Team's exclusive Financial Technology Platform Partner, Adyen powers Alpine's new ecommerce platform, making every fan purchase a live proof point. Content, race-week experiences and C-level hospitality then turn that proof into senior customer conversations, and the Team's partner network opens doors to new business.",
      { x: L, y: 1.95, w: lw, h: 1.9, fontSize: 12.5, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    label(s, "Alpine fans vs. the average internet user", L, 4.05, lw);
    const aud = [["10.0M", "senior decision-makers", "2.22x"], ["23.6M", "business decision-makers", "1.88x"], ["5.6M", "company owners, founders", "1.98x"],
      ["4.5M", "technology early adopters", "3.02x"], ["24.3M", "Google Pay users", "1.83x"], ["7.2M", "Apple Pay users", "1.59x"]];
    const aw = (lw - 0.4) / 3, ah = 1.08;
    aud.forEach(([big, lab, idx], i) => {
      const ax = L + (i % 3) * (aw + 0.2), ay = 4.38 + Math.floor(i / 3) * (ah + 0.15);
      card(s, ax, ay, aw, ah);
      s.addText([{ text: big + " ", options: { fontSize: 18, color: C.text1 } }, { text: idx, options: { fontSize: 11, bold: true, color: C.accent2 } }],
        { x: ax + 0.18, y: ay + 0.12, w: aw - 0.36, h: 0.42, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: ax + 0.18, y: ay + 0.58, w: aw - 0.36, h: 0.4, fontSize: 10.5, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    const x = 7.1, w = R - x, ih = 2.5;
    await photo(s, "alpine_engine.jpg", x, 1.95, w, ih, "Alpine car with Adyen branding on the engine cover (mock-up)");
    s.addText("Alpine mock-up: Adyen on the engine cover", { x, y: 1.95 + ih + 0.06, w, h: 0.25, fontSize: 9.5, color: C.accent3, margin: 0, isTextBox: true });
    const facts = [["Exclusive", "Financial Technology Platform Partner"], ["2027–2029", "three years, global rights"],
      ["£10.0M", "fee in 2027, +5% a year"], ["56", "Paddock Club tickets a year"]];
    const fw = (w - 0.2) / 2, fh = 0.8;
    facts.forEach(([big, lab], i) => {
      const fx = x + (i % 2) * (fw + 0.2), fy = 4.88 + Math.floor(i / 2) * (fh + 0.15);
      card(s, fx, fy, fw, fh, i === 2 ? C.text1 : C.background2);
      s.addText([{ text: big, options: { fontSize: 15, bold: true, color: i === 2 ? C.accent1 : C.text1, breakLine: true } },
        { text: lab, options: { fontSize: 10, color: i === 2 ? C.accent4 : C.text2 } }],
      { x: fx + 0.18, y: fy, w: fw - 0.36, h: fh, margin: 0, isTextBox: true, valign: "middle" });
    });
  }
  {
    const s = content("CONTENT", SECTIONS[4], "05 The opportunities · Route 2 · Business opportunity",
      t("Alpine: Adyen **powers the Team's commerce**, then turns that proof into relationships"),
      "Source: Alpine Formula One Team, Provisional Rights Overview 2027–2029: marketing framework and appendix.",
      "Four pillars: Power the experience (rows 1-2), Prove the performance (rows 3-4), Bring it to life (row 5), Accelerate relationships (rows 6-7). The Partner Forum facilitates introductions without guaranteeing procurement outcomes. Rewards are subject to promotional and regulatory controls.");
    const steps = [["1  Integrate", "Power the experience"], ["2  Prove", "Prove the performance"], ["3  Experience", "Bring it to life"],
      ["4  Convert", "Accelerate relationships"]];
    const sw = (CW + 0.15 * 3) / 4;
    steps.forEach(([head, sub], i) => {
      const x = L + i * (sw - 0.15);
      s.addShape(i === 0 ? S.PENTAGON : S.CHEVRON, { x, y: 1.92, w: sw, h: 0.6, fill: { color: i === 0 ? C.accent1 : i === 3 ? C.text1 : C.accent5 },
        line: { color: C.background1, width: 1.5 } });
      s.addText([{ text: head, options: { bold: true, color: i === 0 ? C.text1 : C.background1, fontSize: 11.5, breakLine: true } },
        { text: sub, options: { color: i === 0 ? C.text1 : C.accent4, fontSize: 10 } }],
      { x: x + 0.4, y: 1.92, w: sw - 0.75, h: 0.6, margin: 0, isTextBox: true, valign: "middle" });
    });
    const rows = [[hc("Alpine's business"), hc("Activation"), hc("What Adyen does"), hc("Outcome for Adyen")],
      ...ALPINE_BUSINESS.map(([biz, act, what, out]) => [
        { text: biz, options: { bold: true, color: C.text1, fontSize: 10.5, valign: "middle" } },
        { text: act, options: { bold: true, color: C.accent2, fontSize: 10.5, valign: "middle" } },
        { text: what, options: { color: C.text2, fontSize: 10.5, valign: "middle" } },
        { text: out, options: { color: C.text1, fontSize: 10.5, valign: "middle", fill: { color: C.accent6 } } },
      ])];
    s.addTable(rows, { x: L, y: 2.68, w: CW, colW: [2.45, 2.45, 4.45, 2.78], rowH: [0.36, ...ALPINE_BUSINESS.map(() => 0.53)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.1, 0.03, 0.1], objectName: "Alpine business table" });
  }
  {
    const s = content("CONTENT", SECTIONS[4], "05 The opportunities · Route 2 · Rights overview",
      t("Rights overview: **Alpine F1 Team × Adyen**"),
      "Source: Alpine Formula One Team, Provisional Rights Overview 2027–2029. All rights subject to change; not legally binding.",
      "All benefits are per year of the term unless stated. Paddock Club: 24 tickets at selected races excluding Monaco, Singapore, Austin, Miami, Las Vegas and Abu Dhabi; 16 at Monaco, Singapore, Austin or Abu Dhabi; 8 at Miami; 8 at Las Vegas (56 in total). Championship bonus: 25% (1st), 12.5% (2nd), 6.5% (3rd); maximum 150% should both Drivers' and Constructors' bonuses be achieved.");
    const cols = [
      [["h", "Commercial terms"], ["kv", "Category:", "Financial Technology Platform"],
        ["kv", "Designation:", "Financial Technology Platform Partner (exclusive); Premium Partner (non-exclusive)"],
        ["kv", "Term and territory:", "2027–2029, global"],
        ["kv", "Fee:", "£10.0M (2027), £10.5M (2028), £11.025M (2029); 5% annual escalator"],
        ["kv", "Payment:", "40% on signing (by 15 Feb in later years), 30% by 15 Sep, 30% by 15 Dec"],
        ["kv", "Championship bonus:", "25% / 12.5% / 6.5% for 1st / 2nd / 3rd; maximum 150%"],
        ["kv", "Contracting entity:", "Alpine Racing Ltd."],
        ["h", "Branding (all season)"],
        ["kv", "Race car:", "engine cover (middle lower); halo top back (one side)"],
        ["kv", "Showcar and virtual car:", "all showcars; the official F1 game (EA)"],
        ["kv", "Kit:", "driver suit and mechanics suit collar*; driver and mechanics helmet chin; team kit collar, one side*"],
        ["kv", "Partner stack:", "HQ, transporters, motorhome, hospitality, media backdrop, garage, website"],
        ["note", "*Race kit as soon as feasible in 2027; team kit on polos in 2027, full collection from 2028."]],
      [["h", "IP rights"], ["b", "Team property, imagery and footage on marketing materials, subject to approval"],
        ["h", "Appearances (per year)"],
        ["kv", "F1 drivers:", "3 × 1-hour race-weekend off-track; 2 × 4-hour marketing"],
        ["kv", "Reserve driver:", "2 × 1-hour race-weekend; 1 × 4-hour marketing"],
        ["kv", "Senior team member:", "2 × 1-hour race-weekend; 2 × 4-hour marketing; 1 × 6-hour conference"],
        ["h", "Integration and content"],
        ["b", "Product integration and in-market activation"],
        ["b", "Partner content capture day; 2 social media campaigns; case studies"],
        ["b", "4 newsletter content blocks; 2 solus CRM emails"],
        ["h", "Launch and servicing"],
        ["b", "Joint launch with press release and social post; dedicated account manager; media reporting (Nielsen, Blinkfire)"]],
      [["h", "Hospitality (per year)"],
        ["kv", "Paddock Club:", "56 tickets: 24 at selected races, 16 at Monaco, Singapore, Austin or Abu Dhabi, 8 at Miami, 8 at Las Vegas; more at partner rate"],
        ["kv", "Also:", "grandstand tickets at partner rate; one-day paddock passes on request; 2 U.S. near-track dinners (15 guests)"],
        ["h", "Off-track experiences"],
        ["kv", "Enstone:", "2 VIP factory tours (12 guests) and 1 factory event (60 guests), at Alpine's cost"],
        ["kv", "Assets:", "showcar and Trak Racer simulators, 14 days' hire each at Adyen's cost"],
        ["kv", "Driving:", "1 motorsport driving day for 24 guests at Alpine's cost; more to buy, e.g. Lapland Ice Driving"],
        ["kv", "Network:", "introductions to Alpine's partners; 6 car-launch tickets"],
        ["h", "Merchandise"],
        ["b", "Polos and caps: 40 signed and 80 unsigned of each; 2 replica helmets, 50 mini helmets, 2 replica driver sets"]],
    ];
    rightsColumns(s, cols, 1.95, 4.9, [L, L + 4.15, L + 8.3], [3.85, 3.85, 3.83], 10.5);
  }

  // ---------- Route 3: Ferrari (placeholders until the proposal arrives)
  {
    const s = content("CONTENT_PHOTO", SECTIONS[4], "05 The opportunities · Route 3 · Scuderia Ferrari",
      [{ text: "Scuderia Ferrari: " }, { text: "[ADD: one-line positioning]", options: { color: C.accent3, italic: true } }],
      "Source: [ADD: Ferrari proposal]",
      "Ferrari overview. Left blank until Ferrari's proposal arrives. Mirror the Max and Alpine overviews: positioning, a short narrative, headline numbers and key facts.");
    const x = 5.35, w = R - x;
    ph(s, x, 1.95, w, 1.9, "Narrative: why Ferrari, and what Adyen would power", { size: 12, align: "left" });
    label(s, "Headline numbers", x, 4.05, w);
    const tw = (w - 0.5) / 3;
    for (let k = 0; k < 3; k++) {
      const tx = x + k * (tw + 0.25);
      card(s, tx, 4.38, tw, 1.15);
      s.addText("[ADD]", { x: tx + 0.25, y: 4.48, w: tw - 0.5, h: 0.5, fontSize: 24, color: C.accent3, margin: 0, isTextBox: true, valign: "top" });
      s.addText(add("number and label", 11), { x: tx + 0.25, y: 5.0, w: tw - 0.5, h: 0.4, margin: 0, isTextBox: true, valign: "top" });
    }
    label(s, "Key facts", x, 5.75, w);
    ph(s, x, 6.05, w, 0.6, "Designation · term · territory · fee", { size: 11, align: "left" });
  }
  {
    const s = content("CONTENT", SECTIONS[4], "05 The opportunities · Route 3 · Business opportunity",
      [{ text: "Ferrari: " }, { text: "[ADD: where Adyen sits in Ferrari's business]", options: { color: C.accent3, italic: true } }],
      "Source: [ADD]",
      "Ferrari business opportunity. Same columns as Max and Alpine so the routes compare like for like.");
    const blank = () => ({ text: "[ADD]", options: { italic: true, color: C.accent3, fontSize: 11, valign: "middle" } });
    const rows = [[hc("Ferrari's business"), hc("Adyen products"), hc("What it does"), hc("Can Adyen run it?")],
      ...[0, 1, 2, 3, 4].map(() => [blank(), blank(), blank(), blank()])];
    s.addTable(rows, { x: L, y: 2.0, w: CW, colW: [3.2, 2.2, 3.15, 3.58], rowH: [0.4, 0.62, 0.62, 0.62, 0.62, 0.62],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.04, 0.1, 0.04, 0.1], objectName: "Ferrari business table" });
  }
  {
    const s = content("CONTENT", SECTIONS[4], "05 The opportunities · Route 3 · Rights package",
      [{ text: "Rights package: " }, { text: "Scuderia Ferrari × Adyen", options: { color: C.accent1 } }],
      "Source: [ADD: Ferrari proposal]",
      "Ferrari rights package. Use the same three columns as the Alpine and Max rights slides.");
    const heads = [["Commercial terms", "Category, designation, term, fee, payment schedule"], ["Branding and IP", "Car, kit, team environment; IP rights"],
      ["Hospitality and experiences", "Paddock Club, factory, driving, merchandise"]];
    heads.forEach(([h, lab], i) => {
      const x = L + i * 4.15;
      label(s, h, x, 2.0, 3.85, C.accent2);
      ph(s, x, 2.35, 3.85, 4.3, lab, { size: 12, align: "left" });
    });
  }

  // ================================================================ 06 Recommendation
  pres.addSection({ title: SECTIONS[5] });
  await divider(6, "Our recommendation", "The preferred route, how Adyen integrates, the value and the investment",
    "adyen_instore.jpg", "Section 6 closes the case: which route, why, where Adyen sits in the business, what it costs and what happens next.");

  // Assessment
  {
    const s = content("CONTENT", SECTIONS[5], "06 Recommendation · Assessment",
      [{ text: "Why we recommend " }, { text: "[ADD: route]", options: { color: C.accent1 } }],
      "Source: SPORTFIVE assessment against Adyen's partnership brief; rights-holder proposals.",
      "Evidence in each cell comes from the proposals. Rate each route ● strong, ◐ partial, ○ weak before the meeting. Ferrari to add.");
    const crit = [...BRIEF_CRITERIA, "Fits the investment envelope", "Payments category available"];
    const ev = {
      max: ["Verstappen Travel ticketing and trailers fit directly; the online store is held by Fanatics; app and sim are new builds",
        "Grandstand ticketing (Spa, Austria 2027) and trackside merchandise",
        "Garage tour, track day and paddock meet-and-greets; Paddock Club to be added",
        "Max's personal business ecosystem; no team partner network",
        "Top follower markets: USA, Brazil, Netherlands, Mexico, UK, Germany",
        "Fee to add", "Non-exclusive ambassador rights"],
      alp: ["Powers agreed parts of the Team's new ecommerce platform",
        "Checkout, rewards and race-week venue payments; KPIs proposed",
        "56 Paddock Club tickets a year, Enstone events, near-track dinners",
        "Introductions to 42 Team partners; One Platform Partner Forum",
        "Global rights; races across all of Adyen's regions",
        "£10.0M in 2027, rising 5% a year", "Exclusive Financial Technology Platform category"],
    };
    const rate = { text: "[ ● ◐ ○ ]  ", options: { bold: true, color: C.accent3 } };
    const cell = (txt) => ({ text: [rate, { text: txt, options: { color: C.text1 } }], options: { fontSize: 10, valign: "middle" } });
    const rows = [[hc("Criterion", { fontSize: 12 }), ...ROUTE_NAMES.map((r) => hc(r, { align: "center", fontSize: 12 }))],
      ...crit.map((c, i) => [
        { text: c, options: { color: C.text1, fontSize: 11.5, bold: true, valign: "middle", fill: { color: C.background2 } } },
        cell(ev.max[i]), cell(ev.alp[i]),
        { text: "[ADD ● ◐ ○ + evidence]", options: { italic: true, color: C.accent3, fontSize: 10, align: "center", valign: "middle" } },
      ])];
    s.addTable(rows, { x: L, y: 1.95, w: CW, colW: [3.13, 3.4, 3.4, 2.2], rowH: [0.42, ...crit.map(() => 0.5)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.1, 0.03, 0.1], objectName: "Assessment table" });
    card(s, L, 6.05, CW, 0.62, C.text1, "Recommendation strip");
    s.addText([{ text: "Our recommendation  ", options: { bold: true, color: C.accent1 } },
      { text: "[ADD: route], because [ADD: one-line rationale]", options: { italic: true, color: C.background1 } }],
    { x: L + 0.3, y: 6.05, w: CW - 0.6, h: 0.62, fontSize: 14, margin: 0, valign: "middle", isTextBox: true });
  }

  // Business integration
  {
    const s = content("CONTENT", SECTIONS[5], "06 Recommendation · Business integration",
      [{ text: "Where Adyen sits " }, { text: "inside [ADD: route]'s business", options: { color: C.accent1 } }],
      "Source: Adyen ('Racing | Unified Payments': unified commerce value chain); [ADD] partner detail.",
      "Integration first, not a logo deal. Top: Adyen's own racing value chain, one platform from fan to business bank account. Replace each [ADD] with the flows, KPIs, races and partners agreed with the chosen rights-holder.");
    await fit(s, "adyen_value_chain.png", L, 1.85, 7.4, 1.9, "Adyen unified commerce value chain, from fan to business bank account");
    const tx = 8.35, tw2 = R - tx;
    s.addText([{ text: "One platform, end to end", options: { bold: true, color: C.text1, fontSize: 14, breakLine: true } },
      { text: "Adyen already runs the whole payment journey for its clients: gateway, risk, authentication, processing, acquiring and reconciliation, online and in person.",
        options: { color: C.text2, fontSize: 12 } }], { x: tx, y: 2.05, w: tw2, h: 1.7, margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 4 });
    const steps = [
      ["FiCreditCard", "Power", "Adyen runs the partner's payments across ticketing, ecommerce, merchandise and hospitality.", "Which flows Adyen powers"],
      ["FiBarChart2", "Prove", "Live volumes and conversion data become a flagship, client-facing case study.", "KPIs to report"],
      ["FiUsers", "Host", "Hospitality at the centre, connecting clients across the partner's ecosystem.", "Races, guests, format"],
      ["FiShare2", "Connect", "Access to the partner's commercial network turns into qualified pipeline.", "Target partners and accounts"],
    ];
    const sw = (CW - 0.9) / 4, y = 3.92, h = 2.1;
    for (const [i, [ic, name, body, ph1]] of steps.entries()) {
      const x = L + i * (sw + 0.3);
      card(s, x, y, sw, h);
      await iconDot(s, ic, x + 0.22, y + 0.18, 0.42);
      s.addText(`${i + 1}  ${name}`, { x: x + 0.75, y: y + 0.18, w: sw - 0.95, h: 0.42, fontSize: 15, bold: true, color: C.text1, margin: 0,
        isTextBox: true, valign: "middle" });
      s.addText(body, { x: x + 0.22, y: y + 0.7, w: sw - 0.44, h: 0.85, fontSize: 10.5, color: C.text2, margin: 0, valign: "top", isTextBox: true });
      ph(s, x + 0.18, y + h - 0.5, sw - 0.36, 0.38, ph1, { size: 10 });
    }
    soWhat(s, "**integration first, not a logo deal.** Every route is tested on how deeply Adyen sits inside the partner's commercial operations.", 6.15);
  }

  // Line to revenue
  {
    const s = content("CONTENT", SECTIONS[5], "06 Recommendation · Value",
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
      ["+36.6%", "F&B revenue at RSC Anderlecht", "after moving the whole matchday fan journey to digital payments with Adyen.", "adyen_stadium.jpg"],
      ["1 platform", "for every FC Bayern payment", "across ticketing, retail, lifestyle and streaming, with new insight into fan behaviour.", "adyen_fans.jpg"],
    ];
    for (const [i, [big, head, body, img]] of proof.entries()) {
      const y = 2.35 + i * 2.2;
      await photo(s, img, x, y, w, 1.95, "Adyen in sport");
      s.addShape(S.RECTANGLE, { x, y, w, h: 1.95, fill: { color: C.text1, transparency: 18 }, line: { color: C.text1, width: 0 } });
      s.addText(big, { x: x + 0.3, y: y + 0.22, w: w - 0.6, h: 0.6, fontSize: 30, color: C.accent1, margin: 0, isTextBox: true, valign: "top" });
      s.addText([{ text: head, options: { bold: true, color: C.background1, breakLine: true } }, { text: body, options: { color: C.accent4 } }],
        { x: x + 0.3, y: y + 0.9, w: w - 0.6, h: 0.95, fontSize: 12, margin: 0, isTextBox: true, valign: "top" });
    }
  }

  // Investment and next steps
  {
    const s = content("CONTENT", SECTIONS[5], "06 Recommendation · Investment and next steps",
      t("Investment and **next steps**"),
      "Source: Adyen budget guidance; GlobalData (average annual value of new F1 deals, 2025); Alpine Provisional Rights Overview 2027–2029.",
      "Budget guidance from Adyen: $10M a year is defensible, $20M needs a very strong case, and a $5-7M option shows how it works. The dashed line marks the average annual value of a new F1 sponsorship deal in 2025 ($5.78M). Alpine's fee is in GBP and is shown as quoted, not converted. Both options are to be presented in the week of 9 November, ahead of 2027.");
    label(s, "Investment envelope (per year)", L, 2.0, 7);
    const opts = [["Prove the model", "$5–7M", 7, 5], ["Defensible core", "$10M", 10, null], ["Flagship", "$20M", 20, null]];
    const bx = L + 2.0, bw = 4.75, max = 20;
    opts.forEach(([name, val, hi, lo], i) => {
      const y = 2.45 + i * 1.0;
      s.addText(name, { x: L, y, w: 1.9, h: 0.42, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      s.addShape(S.RECTANGLE, { x: bx, y: y + 0.06, w: bw, h: 0.3, fill: { color: C.background2 }, line: { color: C.background2, width: 0 } });
      if (lo) s.addShape(S.RECTANGLE, { x: bx, y: y + 0.06, w: (bw * lo) / max, h: 0.3, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
      s.addShape(S.RECTANGLE, { x: bx + (lo ? (bw * lo) / max : 0), y: y + 0.06, w: (bw * (hi - (lo || 0))) / max, h: 0.3,
        fill: { color: lo ? C.accent6 : C.accent1 }, line: { color: C.accent1, width: lo ? 1 : 0 } });
      s.addText(val, { x: bx + (bw * hi) / max + 0.1, y, w: 0.9, h: 0.42, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      s.addText(add("What this level buys", 10.5), { x: bx, y: y + 0.45, w: bw, h: 0.3, margin: 0, isTextBox: true, valign: "top" });
    });
    const mx = bx + (bw * 5.78) / max;
    opts.forEach((_, i) => s.addShape(S.LINE, { x: mx, y: 2.45 + i * 1.0 - 0.02, w: 0, h: 0.46,
      line: { color: C.text1, width: 1.25, dashType: "dash" } }));
    s.addShape(S.LINE, { x: L, y: 5.5, w: 0.3, h: 0, line: { color: C.text1, width: 1.25, dashType: "dash" } });
    s.addText("Average annual value of a new F1 deal, 2025: $5.78M", { x: L + 0.4, y: 5.36, w: 5.5, h: 0.28, fontSize: 10.5,
      color: C.text2, margin: 0, isTextBox: true, valign: "middle" });
    label(s, "On the table", L, 5.8, 7);
    s.addText([{ text: "Alpine: ", options: { bold: true, color: C.text1 } }, { text: "£10.0M in 2027, +5% a year (£31.5M over 2027–29).   ", options: { color: C.text2 } },
      { text: "Max: ", options: { bold: true, color: C.text1 } }, ...add("fee", 11), { text: "   Ferrari: ", options: { bold: true, color: C.text1 } }, ...add("fee", 11)],
    { x: L, y: 6.08, w: 7.3, h: 0.3, fontSize: 11, margin: 0, isTextBox: true, valign: "top" });

    const x = 8.2, w = R - x;
    label(s, "Next steps", x, 2.0, w);
    const steps = [["Chairman reviews the Max and Alpine routes", "Week of 9 November 2026"], ["Headline terms agreed with the rights-holder", null],
      ["Contract and integration plan", null], ["Launch", null]];
    s.addShape(S.LINE, { x: x + 0.14, y: 2.55, w: 0, h: 2.8, line: { color: C.accent4, width: 1.5 } });
    steps.forEach(([st, when], i) => {
      const y = 2.4 + i * 0.92;
      s.addShape(S.OVAL, { x, y, w: 0.28, h: 0.28, fill: { color: C.accent1 }, line: { color: C.background1, width: 2 } });
      s.addText(st, { x: x + 0.5, y: y - 0.05, w: w - 0.5, h: 0.38, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });
      s.addText(when ? [{ text: when, options: { color: C.accent2, bold: true, fontSize: 11 } }] : add("date and owner", 11),
        { x: x + 0.5, y: y + 0.33, w: w - 0.5, h: 0.3, margin: 0, isTextBox: true, valign: "top" });
    });
    card(s, L, 6.45, CW, 0.45, C.text1, "Decision strip");
    s.addText([{ text: "Decision needed  ", options: { bold: true, color: C.accent1 } },
      { text: "[ADD: the approval you are asking the Chairman for]", options: { italic: true, color: C.background1 } }],
    { x: L + 0.3, y: 6.45, w: CW - 0.6, h: 0.45, fontSize: 13, margin: 0, valign: "middle", isTextBox: true });
  }

  // ================================================================ Appendix
  pres.addSection({ title: "Appendix" });
  {
    const s = content("CONTENT", "Appendix", "Appendix", t("Sources and notes"), "Prepared by SPORTFIVE for Adyen. Data as supplied; not independently verified unless stated.",
      "Keep this slide: it answers 'where does that number come from?' in the room.");
    const src = [
      ["GWI", "Global F1 audience 2022–2026; F1 audience by Adyen office market; sport affinity indices; team fans working in financial services (2026, North America and Europe); Alpine fan audience (GWI Core, Q3 2025–Q2 2026). Indices are not percentages."],
      ["GlobalData", "F1 sponsorship 2020–2025: new deals only, excluding renewals. Total deal value is not annual sponsorship revenue."],
      ["Kantar", "BrandZ 2026 Most Valuable Global Brands; Strong Brands Portfolio 2006–2026; IBM and American Express brand spotlights; Kantar × Google 2026 (European companies)."],
      ["SPORTFIVE", "Competitor scan (not exhaustive); team partner networks: combined revenue, market-cap tiers and sector mapping (public data and estimates; figures being re-checked); F1 partner case studies; Airwallex × McLaren credentials."],
      ["Rights holders", "Alpine Formula One Team, Provisional Rights Overview 2027–2029 (not legally binding). Max Verstappen × Adyen rights package (for discussion). Ferrari proposal to follow."],
      ["Adyen", "Office locations (28 cities, 22 markets); FC Bayern and RSC Anderlecht case studies; partnership brief; 'Racing | Unified Payments' imagery."],
      ["F1 calendar", "2027 race locations as supplied to SPORTFIVE; calendar not independently confirmed."],
    ];
    src.forEach(([h, b], i) => {
      const y = 1.95 + i * 0.7;
      if (i) s.addShape(S.LINE, { x: L, y: y - 0.08, w: CW, h: 0, line: { color: C.accent4, width: 0.75 } });
      s.addText(h, { x: L, y, w: 2.2, h: 0.6, fontSize: 12.5, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });
      s.addText(b, { x: L + 2.4, y, w: CW - 2.4, h: 0.6, fontSize: 11, color: C.text2, margin: 0, valign: "top", isTextBox: true });
    });
  }

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
