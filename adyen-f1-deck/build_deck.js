// Adyen x Formula 1: Chairman deck.
// v3: storyline Why F1 > audience > footprint > hospitality as a commercial engine > how Adyen powers the
// business of F1 > ROI > the routes (Max Verstappen, Alpine, Ferrari) > next steps. Visual-first layouts
// using Adyen, team-deck and Verstappen imagery. Ferrari detail, the route assessment and the KPI slide
// are kept as hidden slides.
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
async function fit(s, file, x, y, w, h, alt, align = "center") {
  if (!dims[file]) dims[file] = await sharp(A(file)).metadata();
  const { width, height } = dims[file];
  const r = Math.min(w / width, h / height);
  const iw = width * r, ih = height * r;
  const ix = align === "left" ? x : x + (w - iw) / 2;
  s.addImage({ path: A(file), x: ix, y: y + (h - ih) / 2, w: iw, h: ih, altText: alt || "" });
  return { x: ix, y: y + (h - ih) / 2, w: iw, h: ih };
}

// ------------------------------------------------------------------ layouts
let PHOTO_ICON;
const SECTIONS = ["Why Formula 1", "Hospitality: F1's commercial engine", "Adyen powers the business of F1", "The routes"];
const SHORT = ["Why F1", "Hospitality", "Adyen in F1", "The routes"];

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
      { placeholder: { options: { name: "num", type: "body", x: L, y: 1.4, w: 4, h: 1.3, fontSize: 80, bold: true,
          color: C.accent1, margin: 0, valign: "top" }, text: "01" } },
      { placeholder: { options: { name: "title", type: "title", x: L, y: 2.85, w: 7.3, h: 1.5, fontSize: 38, color: C.background1,
          margin: 0, valign: "top", align: "left" }, text: "Section title" } },
      { placeholder: { options: { name: "desc", type: "body", x: L, y: 4.5, w: 7.0, h: 1.1, fontSize: 18, color: C.accent4,
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

// a dashed box the team fills in (used only on hidden slides)
function ph(s, x, y, w, h, label, { dark = false, size = 12, align = "center" } = {}) {
  s.addShape(S.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.06, fill: { color: dark ? C.accent5 : C.background1 },
    line: { color: C.accent3, width: 1, dashType: "dash" }, objectName: "Placeholder" });
  s.addText([{ text: "[ADD] ", options: { bold: true, color: dark ? C.accent1 : C.accent2 } },
    { text: label, options: { italic: true, color: dark ? C.accent4 : C.text2 } }],
  { x: x + 0.12, y, w: w - 0.24, h, fontSize: size, align, valign: "middle", margin: 0, isTextBox: true, objectName: "Placeholder text" });
}

function label(s, text, x, y, w, color = C.text2) {
  s.addText(text.toUpperCase(), { x, y, w, h: 0.26, fontSize: 10.5, bold: true, color, charSpacing: 1.2, margin: 0,
    isTextBox: true, valign: "top" });
}

function soWhat(s, text, y = 6.15, x = L, w = CW) {
  card(s, x, y, w, 0.58, C.accent6, "So what");
  s.addText([{ text: "So what  ", options: { bold: true, color: C.accent2 } }, ...t(text).map((r) => ({
    text: r.text, options: { color: C.text1, bold: !!r.options } }))],
  { x: x + 0.25, y, w: w - 0.5, h: 0.58, fontSize: 13, valign: "middle", margin: 0, isTextBox: true });
}

async function iconDot(s, name, x, y, d = 0.5, bg = C.accent1, fg = "FFFFFF") {
  s.addShape(S.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { color: bg, width: 0 } });
  const p = d * 0.24;
  s.addImage({ data: await icon(name, fg), x: x + p, y: y + p, w: d - 2 * p, h: d - 2 * p });
}

// big number + caption, no card
function stat(s, x, y, w, big, cap, { size = 30, color = C.text1, capColor = C.text2, capSize = 11.5 } = {}) {
  s.addText(big, { x, y, w, h: size / 60, fontSize: size, bold: true, color, margin: 0, isTextBox: true, valign: "top" });
  s.addText(cap, { x, y: y + size / 60 + 0.04, w, h: 0.5, fontSize: capSize, color: capColor, margin: 0, isTextBox: true, valign: "top" });
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
    s.addShape(S.LINE, { x: L + i * tw, y: 6.25, w: tw - 0.12, h: 0, line: { color: on ? C.accent1 : C.accent5, width: 2 } });
    s.addText([{ text: String(i + 1).padStart(2, "0") + "  ", options: { bold: true, color: on ? C.accent1 : C.accent3 } },
      { text: name, options: { color: on ? C.background1 : C.accent3, bold: on } }],
    { x: L + i * tw, y: 6.35, w: tw - 0.12, h: 0.35, fontSize: 11, margin: 0, isTextBox: true, valign: "top" });
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

// text columns of rights: items are ["h", text] | ["kv", label, text] | ["b", text] | ["note", text]
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
    ["FS&I", [6, 4, 4, 6, 5, 4, 3, 2, 2, 3, 1]],
    ["IT&I", [17, 9, 4, 7, 6, 7, 12, 8, 6, 5, 2]],
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
const GDP = [["Public brands in F1", 10.0], ["Germany", 5.3], ["Japan", 4.5], ["India", 4.5], ["United Kingdom", 4.2], ["France", 3.5]];

// ------------------------------------------------------------------ data (routes)
const MAX_BUSINESS = [ // team deck slide 29, as written: business, Adyen products, what it does, can Adyen run it, verdict
  ["Verstappen.com online store", "Online Payments, Payment Methods", "Merchandise",
    "No, not without Fanatics. Fanatics runs the store under an exclusive deal and controls checkout.", "no"],
  ["Verstappen Travel: Orange Army grandstands (Austria, Spa, Hungary)", "Online Booking, Online Payments", "Ticket sales",
    "Yes, most direct fit. Needs Verstappen.com's ticketing provider to connect to Adyen.", "yes"],
  ["Verstappen Travel: trailers (Austria, Spa, Hungary)", "Tap to Pay", "Merchandise trackside",
    "Yes, most direct fit. Needs Verstappen.com's payment provider to connect to Adyen.", "yes"],
  ["Verstappen Racing (GT3)", "", "Potential trackside merchandise", "Possible.", "maybe"],
  ["Verstappen Racing (esports)", "", "Weekly Twitch streams. Competition races.", "Possible. \"Powered by Adyen\".", "maybe"],
  ["Verstappen Racing Pro Simulation (driver development)", "", "Currently in the works. AI subscription-based driver development program.",
    "Possible. No payment today, so it would be a new build.", "maybe"],
  ["Verstappen News", "", "Database", "Possible. No payment today, so it would be a new build.", "maybe"],
  ["Verstappen official app (currently free: news, stats, alerts, and a link to the shop)", "",
    "Adds one-tap purchase in the app for merchandise, grandstand tickets and experiences.",
    "Possible. The app has no payments today, so it would be a new build.", "maybe"],
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
  {
    const s = pres.addSlide({ masterName: "COVER", sectionTitle: "Introduction" });
    await photo(s, "adyen_kerb.jpg", 7.0, 0, W - 7.0, H, "Race track kerb");
    s.addText("PARTNERSHIP PROPOSAL", { placeholder: "eyebrow" });
    s.addText([{ text: "Adyen ×", options: { breakLine: true } }, { text: "Formula 1", options: { color: C.accent1 } }], { placeholder: "title" });
    s.addText("Why F1 is the right platform for Adyen, and how to win in it", { placeholder: "subtitle" });
    s.addText("Prepared by SPORTFIVE for the Chairman of Adyen  ·  November 2026", { placeholder: "meta" });
    s.addNotes("Cover. Photo: Adyen 'Racing | Unified Payments' deck.");
  }

  // Adyen's brief (team deck slide 2)
  {
    const s = pres.addSlide({ masterName: "STATEMENT", sectionTitle: "Introduction" });
    await photo(s, "earth.jpg", 0, 0, W, H, "Earth from orbit");
    s.addShape(S.RECTANGLE, { x: 0, y: 0, w: W, h: H, fill: { color: C.text1, transparency: 30 }, line: { color: C.text1, width: 0 } });
    s.addText("ADYEN'S BRIEF", { placeholder: "eyebrow" });
    s.addText(t("Adyen: creating **financial efficiencies** in F1"), { placeholder: "title" });
    s.addText("WHAT ADYEN WANTS FROM F1", { x: L, y: 2.75, w: 11, h: 0.3, fontSize: 12, bold: true,
      color: C.accent4, charSpacing: 1.5, margin: 0, isTextBox: true });
    const pr = [
      ["FiCreditCard", "Payment integration", "Adyen's payments live inside the team's or rights holder's business"],
      ["FiGlobe", "Global brand", "Show how Adyen's payments can power the financial business of F1"],
      ["FiUsers", "Client relationships", "Host partners, merchants and senior decision makers"],
      ["FiTrendingUp", "Commercial growth", "Win new deals, renew contracts and build pipeline"],
      ["FiFlag", "One global programme", "Unite local hosting across an initial 8–10 F1 races"],
    ];
    const cw = (CW - 1.0) / 5;
    for (const [i, [ic, head, body]] of pr.entries()) {
      const x = L + i * (cw + 0.25), y = 3.25;
      card(s, x, y, cw, 2.75, i === 0 ? C.accent2 : C.accent5, "Priority card");
      await iconDot(s, ic, x + 0.25, y + 0.28, 0.52, i === 0 ? C.text1 : C.accent1);
      s.addText(head, { x: x + 0.25, y: y + 0.95, w: cw - 0.5, h: 0.62, fontSize: 15, bold: true, color: C.background1, margin: 0,
        isTextBox: true, valign: "bottom" });
      s.addText(body, { x: x + 0.25, y: y + 1.65, w: cw - 0.5, h: 1.0, fontSize: 12, color: i === 0 ? C.background1 : C.accent4, margin: 0, isTextBox: true,
        valign: "top" });
    }
    s.addNotes("Source: Briefing - Adyen x Premium Experiences (Adyen), sections 1–5 and 7.\nAdyen wants a global brand and hospitality proposition that shows how payments power its partners, strengthens relationships with partners and merchants, and supports new deals, renewals and pipeline. The initial target is 8–10 races. The audience includes senior and C-suite decision makers.");
  }

  // Partnership hypothesis (team deck slide 3)
  {
    const s = pres.addSlide({ masterName: "STATEMENT", sectionTitle: "Introduction" });
    await photo(s, "f1_car_blur.jpg", 0, 0, W, H, "F1 car at speed");
    s.addShape(S.RECTANGLE, { x: 0, y: 0, w: W, h: H, fill: { color: C.text1, transparency: 40 }, line: { color: C.text1, width: 0 } });
    s.addText("OUR PARTNERSHIP HYPOTHESIS", { placeholder: "eyebrow" });
    s.addText(t("An F1 partnership can build Adyen's global brand and deepen client relationships through **payments storytelling** and a **global hospitality programme**"),
      { placeholder: "title" });
    s.addNotes("The one sentence the rest of the deck tests.");
  }

  // Two lenses: transaction volume vs the full marketing platform
  {
    const s = content("CONTENT", "Introduction", "How to judge F1",
      t("Judge F1 as a **marketing platform**, not only as transaction volume"),
      "Source: GlobalData (2026); GWI; Max Verstappen × Adyen proposal (Nielsen Sports); SPORTFIVE team partner analysis.",
      "The framing for the whole meeting. Transaction volume is real but it is not the headline; the case is brand, audience, influence, hospitality, network and proof working together.");
    const lw = 3.85;
    card(s, L, 1.95, lw, 4.7, C.background2, "Transaction lens");
    await iconDot(s, "FiCreditCard", L + 0.35, 2.3, 0.7, C.accent3);
    s.addText("The transaction lens", { x: L + 0.35, y: 3.2, w: lw - 0.7, h: 0.45, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText("Payment volume through a team's checkout, tickets and merchandise.", { x: L + 0.35, y: 3.7, w: lw - 0.7, h: 0.9,
      fontSize: 13, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    s.addText("Real, and part of the case. On its own, it undersells F1.", { x: L + 0.35, y: 4.75, w: lw - 0.7, h: 0.9,
      fontSize: 13, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    const x = L + lw + 0.3, w = R - x;
    card(s, x, 1.95, w, 4.7, C.text1, "Platform lens");
    label(s, "The platform lens: what F1 actually delivers", x + 0.35, 2.15, w - 0.7, C.accent1);
    const rows = [
      ["FiAward", "Brand", "50% of the world's most valuable brands are involved in F1"],
      ["FiUsers", "Audience", "#1 sport for all five audiences Adyen sells to"],
      ["FiStar", "Influence", "Max Verstappen: F1's most popular driver, 19M Instagram followers"],
      ["FiCoffee", "Hospitality", "24 race weekends a year to host clients and prospects"],
      ["FiShare2", "Network", "350+ global brands in team partner portfolios"],
      ["FiCheckCircle", "Proof", "Adyen's payments live inside a team's business: an enterprise case study"],
    ];
    for (const [i, [ic, head, body]] of rows.entries()) {
      const ry = 2.6 + i * 0.66;
      await iconDot(s, ic, x + 0.35, ry, 0.46);
      s.addText(head, { x: x + 1.0, y: ry, w: 1.6, h: 0.46, fontSize: 14, bold: true, color: C.background1, margin: 0, isTextBox: true, valign: "middle" });
      s.addText(body, { x: x + 2.6, y: ry, w: w - 2.9, h: 0.46, fontSize: 12.5, color: C.accent4, margin: 0, isTextBox: true, valign: "middle" });
    }
  }

  // Executive summary: the story on one page
  {
    const s = content("CONTENT", "Introduction", "Executive summary",
      t("F1 is a **global commercial engine**, and Adyen can power it"),
      "Source: GWI; GlobalData; Adyen; partner case studies; rights-holder proposals; SPORTFIVE analysis. See Sources and notes.",
      "The storyline in six steps, then the three routes. Each tile is one section of the deck.");
    const tiles = [
      ["01", "Why F1", "625M", "F1 followers in 2026, up 30.8% since 2022"],
      ["02", "Audience", "#1", "sport on all five audiences Adyen sells to"],
      ["03", "Footprint", "457M", "F1 fans in Adyen's 22 office markets"],
      ["04", "Hospitality", "$100M+", "orders Komatsu received at races with Williams"],
      ["05", "Adyen in F1", "4", "payment brands already partner F1 teams; Adyen is not yet in"],
      ["06", "The return", "$300M+", "revenue opportunity HPE accelerated from F1 race activations"],
    ];
    const tw = (7.45 - 0.4) / 3, th = 2.05;
    tiles.forEach(([n, head, big, body], i) => {
      const x = L + (i % 3) * (tw + 0.2), y = 1.95 + Math.floor(i / 3) * (th + 0.2);
      card(s, x, y, tw, th);
      s.addText([{ text: n + "  ", options: { color: C.accent1, bold: true } }, { text: head.toUpperCase(), options: { color: C.text2, bold: true } }],
        { x: x + 0.22, y: y + 0.2, w: tw - 0.44, h: 0.28, fontSize: 10, charSpacing: 1, margin: 0, isTextBox: true });
      s.addText(big, { x: x + 0.22, y: y + 0.55, w: tw - 0.44, h: 0.62, fontSize: 30, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(body, { x: x + 0.22, y: y + 1.22, w: tw - 0.44, h: 0.72, fontSize: 11.5, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    const x = 8.35, w = R - x, y = 1.95, h = 4.3;
    card(s, x, y, w, h, C.text1, "Routes card");
    label(s, "Two routes in, then expand", x + 0.3, y + 0.25, w - 0.6, C.accent1);
    const routes = [
      ["max_thumb.jpg", "Max Verstappen", "Adyen powers the Verstappen ecosystem: ticketing, trackside, simulation"],
      ["alpine_engine.jpg", "Alpine F1 Team", "Exclusive FinTech Platform Partner; Adyen powers the Team's ecommerce"],
      [null, "Then expand", "Once Adyen is in F1, build across the grid from a proven start"],
    ];
    for (const [i, [img, name, body]] of routes.entries()) {
      const ry = y + 0.68 + i * 1.12;
      if (img) await photo(s, img, x + 0.3, ry, 0.85, 0.85, name);
      else {
        s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.3, y: ry, w: 0.85, h: 0.85, rectRadius: 0.06, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
        s.addImage({ data: await icon("FiTrendingUp", "00112C"), x: x + 0.53, y: ry + 0.23, w: 0.39, h: 0.39 });
      }
      s.addText([{ text: name, options: { bold: true, color: C.background1, fontSize: 14, breakLine: true } },
        { text: body, options: { color: C.accent4, fontSize: 10.5 } }],
      { x: x + 1.35, y: ry - 0.02, w: w - 1.6, h: 0.92, margin: 0, isTextBox: true, valign: "top" });
    }
    s.addShape(S.LINE, { x: x + 0.3, y: y + 3.72, w: w - 0.6, h: 0, line: { color: C.accent5, width: 0.75 } });
    s.addText([{ text: "Next  ", options: { bold: true, color: C.accent1 } }, { text: "Chairman review, w/c 9 November", options: { color: C.background1 } }],
      { x: x + 0.3, y: y + 3.8, w: w - 0.6, h: 0.35, fontSize: 11.5, margin: 0, isTextBox: true, valign: "middle" });
  }

  // ================================================================ 01 Why F1
  pres.addSection({ title: SECTIONS[0] });
  await divider(1, "Why Formula 1", "Growth, brand value, audience and footprint", "f1_city.jpg",
    "Section 1: why F1 at all, before any asset is discussed. Photo: team deck cover.");

  // Growth
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why F1 · Growth",
      t("F1 is growing in **audience and in commercial value**"),
      "Source: GWI (global audience, followers); GlobalData (new sponsorship deals only, excl. renewals). 2026 YTD: $1.91B across 139 deals, year incomplete.",
      "Audience: 478.0M (2022) to 625.3M (2026), +30.8%, +147.3M followers; +8.3% vs 2025.\nSponsorship: total value of NEW deals, not annual sponsorship revenue. $0.89B (2020) to $2.37B (2025), +165.3%. 125 new deals in 2025 (+28.9% vs 2020). Average annual value $2.21M to $5.78M (+161.5%).");
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
    soWhat(s, "brands are paying more to be in F1: the average new deal rose from **$2.21M in 2020 to $5.78M in 2025**.");
  }

  // Business leader network (team deck slide 11)
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why F1 · Business leader network",
      t("Half of the world's most valuable brands are **already in F1**"),
      "Source: GlobalData (2026).",
      "Team deck slide 11. 50% of the world's most valuable brands are involved in F1; the public brands in the F1 ecosystem have combined revenue of $10T, more than the GDP of any of the world's third to seventh largest economies.");
    s.addText("50%", { x: L, y: 1.9, w: 2.1, h: 0.9, fontSize: 54, bold: true, color: C.accent1, margin: 0, isTextBox: true, valign: "top" });
    s.addText("of the world's most valuable brands are involved in F1", { x: L + 2.2, y: 2.05, w: 2.6, h: 0.75, fontSize: 13,
      color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    s.addText("$10T", { x: L, y: 2.95, w: 2.1, h: 0.9, fontSize: 54, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    s.addText("combined revenue of the public brands in the F1 ecosystem", { x: L + 2.2, y: 3.1, w: 2.6, h: 0.75, fontSize: 13,
      color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    label(s, "Bigger than these economies' GDP ($T)", L, 4.1, 4.8);
    s.addChart(pres.charts.BAR, [{ name: "$T", labels: GDP.map((g) => g[0]), values: GDP.map((g) => g[1]) }], {
      x: L - 0.1, y: 4.35, w: 4.9, h: 2.45, barDir: "bar", ...chartBase(), catAxisOrientation: "maxMin", barGapWidthPct: 35,
      chartColors: GDP.map((_, i) => (i === 0 ? HEX.green : HEX.context)), dataLabelFormatCode: '"$"0.0"T"', catAxisLabelFontSize: 10.5,
      dataLabelFontSize: 10.5, valAxisMinVal: 0, valAxisMaxVal: 12.5,
    });
    const x = 5.55, w = R - x;
    await fit(s, "f1_logo_wall.png", x, 1.9, w, 3.15, "Logos of global brands involved in F1");
    s.addShape(S.LINE, { x, y: 5.3, w, h: 0, line: { color: C.accent4, width: 0.75 } });
    s.addText([{ text: "5 of the Magnificent 7", options: { bold: true, color: C.text1, fontSize: 16, breakLine: true } },
      { text: "are involved in Formula 1", options: { color: C.text2, fontSize: 12 } }],
    { x, y: 5.5, w: 2.7, h: 0.9, margin: 0, isTextBox: true, valign: "middle" });
    await fit(s, "mag7_logos.png", x + 2.9, 5.5, w - 2.9, 0.9, "Meta, Google, Amazon Web Services, Microsoft and Apple logos");
  }

  // Brand value (Kantar list + strong-brand returns)
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why F1 · Brand value",
      t("The strongest brands **outperform the market**, and many of them race in F1"),
      "Source: Kantar BrandZ 2026 (Top 100, Strong Brands Portfolio, brand spotlights); Kantar × Google 2026. F1 involvement marked by SPORTFIVE.",
      "Left: Kantar BrandZ 2026 Top 100, with the brands the team identified as involved in F1 boxed (40 of 100 as marked; check before quoting a count). IBM and American Express: the team's analysis is that both posted their biggest brand-value increase in the year they entered F1 partnerships.");
    const box = await fit(s, "kantar_list.png", L, 1.85, 4.45, 4.95, "Kantar BrandZ 2026 Top 100 list", "left");
    const top = 25 / 1100, pitch = 18.714 / 1100;
    for (const [a, b] of KANTAR_GROUPS) {
      const right = a > 50, ra = right ? a - 50 : a, rb = right ? b - 50 : b;
      const fx = right ? 0.495 : 0.03, fw = right ? 0.44 : 0.43;
      const y0 = box.y + box.h * (top + (ra - 1) * pitch - pitch * 0.52), y1 = box.y + box.h * (top + (rb - 1) * pitch + pitch * 0.52);
      s.addShape(S.RECTANGLE, { x: box.x + box.w * fx, y: y0, w: box.w * fw, h: y1 - y0, fill: { color: C.accent1, transparency: 88 },
        line: { color: C.accent1, width: 1.25 }, objectName: "F1 brand highlight" });
    }
    const x = L + box.w + 0.4, w = R - x;
    s.addShape(S.RECTANGLE, { x, y: 1.93, w: 0.3, h: 0.18, fill: { color: C.accent1, transparency: 88 }, line: { color: C.accent1, width: 1.25 } });
    s.addText("Kantar Top 100 brand involved in F1", { x: x + 0.42, y: 1.88, w: w - 0.42, h: 0.28, fontSize: 10.5, color: C.text2, margin: 0, isTextBox: true, valign: "middle" });
    card(s, x, 2.3, w, 1.75, C.text1, "Returns card");
    label(s, "Performance, 2006–2026", x + 0.3, 2.45, w - 0.6, C.accent1);
    const rets = [["504%", "Kantar Strong Brands Portfolio", true], ["451%", "S&P 500", false], ["234%", "MSCI World", false]];
    const rw = (w - 0.6) / 3;
    rets.forEach(([big, lab, on], i) => stat(s, x + 0.3 + i * rw, 2.8, rw - 0.15, big, lab,
      { size: on ? 34 : 28, color: on ? C.accent1 : C.background1, capColor: C.accent4, capSize: 11 }));
    const cards = [["2.3x", "stock-market performance vs the STOXX Europe 600, for the brands with the strongest future power"],
      ["IBM · $150.8B", "brand value, +20% vs 2025. Ferrari partner"], ["AmEx · $80.3B", "brand value, +22% vs 2025. Involved in F1"]];
    const cw = (w - 0.4) / 3;
    cards.forEach(([big, lab], i) => {
      const cx = x + i * (cw + 0.2);
      card(s, cx, 4.25, cw, 1.6);
      s.addText(big, { x: cx + 0.2, y: 4.38, w: cw - 0.4, h: 0.45, fontSize: 17, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: cx + 0.2, y: 4.85, w: cw - 0.4, h: 0.9, fontSize: 10.5, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    soWhat(s, "IBM and American Express both posted their **biggest brand-value gains the year they entered F1**.", 6.05, x, w);
  }

  // Audience fit
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why F1 · Audience",
      t("F1 is the strongest sport for **every audience Adyen sells to**"),
      "Source: GWI. Affinity index; ranking covers the five sports assessed. Benchmark per GWI methodology.",
      "Indices are not percentages. Definitions: high income = highest income segment; owners/founders = own or founded a business; senior decision-makers = influence over workplace purchasing; large company employees = companies with 1,001-5,000 employees; early tech adopters = among the first to adopt new technologies.");
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
    s.addText("F1 ranks #1 on all five. Higher index = stronger over-representation among the sport's fans.",
      { x: L, y: 5.75, w: 8.35, h: 0.3, fontSize: 11, color: C.text2, margin: 0, isTextBox: true });
    const stats = [["237.9", "Early tech adopters", "31% above the next-best sport"], ["166.6", "Senior decision-makers", "12% above the next-best sport"]];
    stats.forEach(([big, head, body], i) => {
      const x = 9.25, y = 2.0 + i * 1.98, w = R - 9.25, h = 1.83;
      card(s, x, y, w, h, i === 0 ? C.text1 : C.background2);
      s.addText(big, { x: x + 0.3, y: y + 0.2, w: w - 0.6, h: 0.7, fontSize: 36, bold: true, color: i === 0 ? C.accent1 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText([{ text: head, options: { bold: true, color: i === 0 ? C.background1 : C.text1, breakLine: true } }, { text: body, options: { color: i === 0 ? C.accent4 : C.text2 } }],
        { x: x + 0.3, y: y + 0.92, w: w - 0.6, h: 0.8, fontSize: 12, margin: 0, isTextBox: true, valign: "top" });
    });
    soWhat(s, "F1 leads on **every audience Adyen needs**, from enterprise buyers to the consumers adopting new ways to pay.");
  }

  // Fans working in financial services (team deck slide 20)
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why F1 · Audience",
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
    const stats = [["172.9", "Mercedes fans", "The highest index of any team"], ["1.80M", "Ferrari fans", "The largest pool working in finance"],
      ["140.1", "Alpine fans", "0.26M fans working in finance"]];
    stats.forEach(([big, head, body], i) => {
      const x = 8.75, w = R - x, y = 2.0 + i * 1.6, h = 1.45;
      card(s, x, y, w, h);
      s.addText(big, { x: x + 0.3, y: y + 0.15, w: w - 0.6, h: 0.55, fontSize: 28, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText([{ text: head, options: { bold: true, color: C.text1, breakLine: true } }, { text: body, options: { color: C.text2 } }],
        { x: x + 0.3, y: y + 0.7, w: w - 0.6, h: 0.65, fontSize: 11.5, margin: 0, isTextBox: true, valign: "top" });
    });
  }

  // Footprint
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why F1 · Footprint",
      t("F1 races **where Adyen already does business**"),
      "Source: F1 2027 calendar and Adyen office list as supplied to SPORTFIVE (calendar not independently confirmed); map: Adyen.",
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
    const x = 10.0, w = R - x;
    await fit(s, "adyen_map.jpg", x, 1.95, w, 1.85, "Adyen global acquiring footprint map");
    const stats = [["24", "Grands Prix in 2027"], ["28", "Adyen offices"], ["7 of 8", "Adyen regions host a race"]];
    stats.forEach(([big, body], i) => {
      const y = 4.0 + i * 0.92;
      s.addShape(S.LINE, { x, y: y - 0.06, w, h: 0, line: { color: C.accent4, width: 0.75 } });
      s.addText(big, { x, y, w: 1.2, h: 0.7, fontSize: 26, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
      s.addText(body, { x: x + 1.25, y, w: w - 1.25, h: 0.7, fontSize: 11.5, color: C.text2, margin: 0, isTextBox: true, valign: "middle" });
    });
  }

  // Priority markets
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why F1 · Footprint",
      t("457M F1 fans live in Adyen's markets, and **India and Japan are accelerating**"),
      "Source: GWI (F1 audience by market, 2026 vs 2022); Adyen (office markets). Growth rates as reported.",
      "All 22 Adyen office markets: combined F1 audience 457.2M in 2026 vs 342.3M in 2022 (+33.6%). 13 of 22 host a 2027 race. Chart shows the 11 largest; the other 11 add 34.4M.");
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
      ["457.2M", "F1 fans in Adyen's 22 office markets", "+33.6% since 2022; 13 of 22 host a 2027 race.", false],
      ["India · 117.4M", "+94.9% since 2022", "Fastest growth of any Adyen market, with no Grand Prix.", true],
      ["Japan · 7.1M", "+41.2% since 2022", "A priority market for Adyen, home of the Suzuka Grand Prix.", true],
    ];
    stats.forEach(([big, head, body, priority], i) => {
      const x = 8.75, w = R - x, y = 2.0 + i * 1.53, h = 1.4;
      card(s, x, y, w, h, i === 0 ? C.text1 : C.background2);
      s.addText(big, { x: x + 0.3, y: y + 0.14, w: w - 0.6, h: 0.5, fontSize: 24, bold: true, color: i === 0 ? C.accent1 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      if (priority) {
        s.addShape(S.ROUNDED_RECTANGLE, { x: x + w - 1.55, y: y + 0.18, w: 1.3, h: 0.28, rectRadius: 0.14, fill: { color: C.accent6 },
          line: { color: C.accent6, width: 0 } });
        s.addText("PRIORITY MARKET", { x: x + w - 1.55, y: y + 0.18, w: 1.3, h: 0.28, fontSize: 8, bold: true, color: C.accent2,
          align: "center", valign: "middle", margin: 0, isTextBox: true });
      }
      s.addText([{ text: head, options: { bold: true, color: i === 0 ? C.background1 : C.text1, breakLine: true } }, { text: body, options: { color: i === 0 ? C.accent4 : C.text2 } }],
        { x: x + 0.3, y: y + 0.65, w: w - 0.6, h: 0.7, fontSize: 11.5, margin: 0, isTextBox: true, valign: "top" });
    });
  }

  // Six data points
  {
    const s = content("CONTENT", SECTIONS[0], "01 Why F1 · What it means for Adyen",
      t("Why F1 makes sense for Adyen, **in six data points**"),
      "Source: GWI; GlobalData; F1; Adyen; SPORTFIVE analysis.",
      "Synthesis of section 1: each card pairs something Adyen needs with the evidence that F1 delivers it.");
    const items = [
      ["FiBriefcase", "Reach enterprise buyers", "166.6", "Senior decision-maker index, the highest of five sports"],
      ["FiZap", "Lead on innovation", "237.9", "Early tech adopter index, 31% above the next-best sport"],
      ["FiGlobe", "Grow in priority markets", "457M", "F1 fans across Adyen's 22 office markets"],
      ["FiCalendar", "Host clients where they are", "13 of 22", "Adyen office markets host a 2027 Grand Prix"],
      ["FiFlag", "Keep pace with the category", "4", "Payment brands already in F1: Stripe, Airwallex, Mastercard, Visa"],
      ["FiTrendingUp", "Invest in a rising asset", "$5.78M", "Average annual value of a new F1 deal in 2025"],
    ];
    const cw = (CW - 0.6) / 3, ch = 2.15;
    for (const [i, [ic, need, big, body]] of items.entries()) {
      const x = L + (i % 3) * (cw + 0.3), y = 2.0 + Math.floor(i / 3) * (ch + 0.25);
      card(s, x, y, cw, ch);
      await iconDot(s, ic, x + 0.3, y + 0.28, 0.46);
      s.addText(need, { x: x + 0.9, y: y + 0.28, w: cw - 1.1, h: 0.46, fontSize: 13, bold: true, color: C.text1, margin: 0,
        valign: "middle", isTextBox: true });
      s.addText(big, { x: x + 0.3, y: y + 0.88, w: cw - 0.6, h: 0.55, fontSize: 28, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(body, { x: x + 0.3, y: y + 1.45, w: cw - 0.6, h: 0.6, fontSize: 12, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    }
  }

  // ================================================================ 02 Hospitality: F1's commercial engine
  pres.addSection({ title: SECTIONS[1] });
  await divider(2, "Hospitality: F1's commercial engine", "Client retention, pipeline generation and merchant acquisition, at the track",
    "paddock_tour.jpg", "Section 2. Photo: paddock tour (Verstappen proposal).");

  // The ultimate B2B platform (team deck slide 13)
  {
    const s = content("CONTENT", SECTIONS[1], "02 Hospitality · The B2B platform",
      t("F1 hospitality turns guests into **retention, pipeline and new merchants**"),
      "Source: SPORTFIVE; team partner portfolios (team deck). Photos: team deck.",
      "Team deck slide 13, the ultimate B2B platform: exclusive experiences, a qualified audience and visibility with a high-value enterprise buyer universe, inside partner portfolios of 350+ global brands.");
    const cols = [
      ["hosp_hotlap.jpg", "FiHeart", "Client retention", "Exclusive experiences", "Bonds with clients that traditional hosting cannot match."],
      ["hosp_suite.jpg", "FiTrendingUp", "Pipeline generation", "A qualified audience", "C-suite decision-makers, in market, at every race."],
      ["hosp_terrace.jpg", "FiUserPlus", "Merchant acquisition", "A network of brands", "Team partner portfolios: 350+ global brands to meet."],
    ];
    const cw = (CW - 0.6) / 3;
    for (const [i, [img, ic, outcome, head, body]] of cols.entries()) {
      const x = L + i * (cw + 0.3);
      await photo(s, img, x, 1.95, cw, 2.35, head);
      await iconDot(s, ic, x + 0.2, 4.05, 0.55);
      s.addText(outcome.toUpperCase(), { x: x + 0.9, y: 4.42, w: cw - 0.9, h: 0.3, fontSize: 11, bold: true, color: C.accent2, charSpacing: 1,
        margin: 0, isTextBox: true });
      s.addText([{ text: head, options: { bold: true, color: C.text1, fontSize: 15, breakLine: true } }, { text: body, options: { color: C.text2, fontSize: 12 } }],
        { x, y: 4.8, w: cw, h: 0.95, margin: 0, isTextBox: true, valign: "top" });
    }
    card(s, L, 5.95, CW, 0.75, C.text1, "Stats strip");
    const strip = [["350+", "global brands in team partner portfolios"], ["24", "race weekends a year to host clients"], ["8–10", "races in Adyen's first global programme"]];
    const sw = CW / 3;
    strip.forEach(([big, lab], i) => s.addText([{ text: big + "  ", options: { bold: true, color: C.accent1, fontSize: 20 } },
      { text: lab, options: { color: C.background1, fontSize: 11.5 } }],
    { x: L + 0.3 + i * sw, y: 5.95, w: sw - 0.4, h: 0.75, margin: 0, isTextBox: true, valign: "middle" }));
  }

  // F1 team case studies (team deck slides 22-23)
  {
    const s = content("CONTENT", SECTIONS[1], "02 Hospitality · Proof from F1 partners",
      t("F1 partners report **real commercial returns** from hosting at races"),
      "Source: Komatsu × Williams, HPE × Mercedes and Businessolver × Alpine published case material, as compiled by SPORTFIVE.",
      "Three partners, three proof points: deals closed at races (Komatsu), revenue opportunity accelerated (HPE) and pipeline influenced (Businessolver, an Alpine partner).");
    const cw = (CW - 0.6) / 3, y = 2.0, h = 4.75;
    const cases = [
      { pair: "Komatsu × Williams", big: "$100M+", lab: "orders received at races",
        body: "Komatsu hosts global stakeholders at races, many at a Komatsu event for the first time.",
        stats: [["3,735", "stakeholders hosted"], ["90%", "found it useful for business"], ["94%", "guest satisfaction"]] },
      { pair: "HPE × Mercedes", big: "$300M+", lab: "revenue opportunity accelerated from race activations alone",
        quote: "\"For us, the real value has been the ability to authentically showcase our technology through Mercedes F1 use cases in advertising, on digital platforms, at strategic events, with press/analysts and through direct customer engagement at races.\"",
        by: "Antonio Neri, CEO, Hewlett Packard Enterprise" },
      { pair: "Businessolver × Alpine", big: "$122M", lab: "business pipeline influenced by at-track hosting and experiences",
        body: "Technology with heart: AI, decision-support and real-time analytics, with pipeline influenced by at-track hosting.",
        tag: "An Alpine partner (Route 2)" },
    ];
    cases.forEach((c, i) => {
      const x = L + i * (cw + 0.3);
      const dark = i === 1;
      card(s, x, y, cw, h, dark ? C.text1 : C.background2);
      s.addText(c.pair.toUpperCase(), { x: x + 0.3, y: y + 0.25, w: cw - 0.6, h: 0.3, fontSize: 11, bold: true, charSpacing: 1,
        color: dark ? C.accent1 : C.accent2, margin: 0, isTextBox: true });
      s.addText(c.big, { x: x + 0.3, y: y + 0.6, w: cw - 0.6, h: 0.75, fontSize: 40, bold: true, color: dark ? C.accent1 : C.text1,
        margin: 0, isTextBox: true, valign: "top" });
      s.addText(c.lab, { x: x + 0.3, y: y + 1.38, w: cw - 0.6, h: 0.55, fontSize: 12.5, bold: true, color: dark ? C.background1 : C.text1,
        margin: 0, isTextBox: true, valign: "top" });
      if (c.body) s.addText(c.body, { x: x + 0.3, y: y + 2.05, w: cw - 0.6, h: 1.0, fontSize: 11.5, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
      if (c.stats) c.stats.forEach(([b, l], k) => {
        const sy = y + 3.15 + k * 0.48;
        s.addText([{ text: b + "  ", options: { bold: true, color: C.text1, fontSize: 15 } }, { text: l, options: { color: C.text2, fontSize: 11 } }],
          { x: x + 0.3, y: sy, w: cw - 0.6, h: 0.42, margin: 0, isTextBox: true, valign: "middle" });
      });
      if (c.quote) {
        s.addText(c.quote, { x: x + 0.3, y: y + 2.05, w: cw - 0.6, h: 1.8, fontSize: 11.5, italic: true, color: C.accent4, margin: 0, isTextBox: true, valign: "top" });
        s.addText(c.by, { x: x + 0.3, y: y + 4.05, w: cw - 0.6, h: 0.45, fontSize: 10.5, bold: true, color: C.background1, margin: 0, isTextBox: true });
      }
      if (c.tag) {
        s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.3, y: y + 3.55, w: cw - 0.6, h: 0.5, rectRadius: 0.08, fill: { color: C.accent6 },
          line: { color: C.accent1, width: 1 } });
        s.addText(c.tag, { x: x + 0.45, y: y + 3.55, w: cw - 0.9, h: 0.5, fontSize: 11, bold: true, color: C.accent2, margin: 0, isTextBox: true, valign: "middle" });
      }
    });
  }

  // Team partnership network (team deck slide 15)
  {
    const s = content("CONTENT", SECTIONS[1], "02 Hospitality · Partner networks",
      t("Mercedes, McLaren and Ferrari bring the **largest partner networks**"),
      "Source: SPORTFIVE analysis. 2024–2025 public data; estimates where no disclosure; some revenues from parent-company segments. USD at 2024–25 average FX.",
      "Partners' total combined revenue by team, and each team's three largest partners by reported annual revenue. Team note: figures being re-checked (GF). Alpine and Ferrari highlighted as the two team routes.");
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
    const s = content("CONTENT", SECTIONS[1], "02 Hospitality · Partner profile",
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
    soWhat(s, "McLaren (6) and Mercedes (5) have the most **mega-cap partners**; 31 of Alpine's 42 are small-cap, 74% private.", 6.25);
  }

  // Partner mapping by sector (team deck slide 17)
  {
    const s = content("CONTENT", SECTIONS[1], "02 Hospitality · Sector mapping",
      t("Financial services already sits in **every team's partner network**"),
      "Source: SPORTFIVE partner mapping. Relevant team partners only, by sector.",
      "Number of relevant team partners by sector. Team note: figures being re-checked (GF).");
    s.addChart(pres.charts.BAR, SECTOR.series.map(([name, vals]) => ({ name, labels: SECTOR.teams, values: vals.map((v) => v || null) })), {
      x: L - 0.1, y: 1.95, w: CW + 0.2, h: 4.15, barDir: "col", barGrouping: "stacked", ...chartBase(),
      chartColors: [HEX.green, HEX.navy, HEX.g1, HEX.g2, HEX.g3], showValue: true, dataLabelPosition: "ctr", dataLabelColor: "FFFFFF",
      dataLabelFontSize: 10, dataLabelFontBold: true, showLegend: true, legendPos: "t", legendFontSize: 10.5, legendFontFace: "+mn-lt",
      legendColor: HEX.slate, barGapWidthPct: 45, catAxisLabelFontSize: 10.5,
    });
    soWhat(s, "every team counts financial-services partners, from 1 (Cadillac) to 6 (McLaren, Williams). **Alpine has 4, Ferrari 5.**", 6.2);
  }

  // ================================================================ 03 Adyen powers the business of F1
  pres.addSection({ title: SECTIONS[2] });
  await divider(3, "Adyen powers the business of F1", "Payments is contested; the winners sit inside the team's business", "adyen_instore.jpg",
    "Section 3: the category, the benchmark, our credentials, where Adyen sits and what it returns.");

  // Payments in F1: who is on the grid, and Adyen's seat
  {
    const s = content("CONTENT", SECTIONS[2], "03 Adyen in F1 · The category",
      t("Payments is one of F1's **most contested categories**"),
      "Source: SPORTFIVE analysis (BI competitor scan). Team names as used in the scan.",
      "Four payment brands already partner F1 teams. Two are Adyen competitors (Stripe at Mercedes, Airwallex at McLaren). Two are card schemes (Mastercard in the McLaren Mastercard team name, Visa in the Visa Cash App Racing Bulls team name). Mastercard and Airwallex already sit side by side at McLaren: schemes and platforms co-exist. Adyen is not yet in F1.");
    // counters
    const counters = [["4", "payment brands partner F1 teams", C.text1], ["2", "are Adyen competitors: Stripe, Airwallex", C.text1],
      ["2", "are card schemes: Mastercard, Visa", C.accent2]];
    const cw3 = (CW - 0.6) / 3;
    counters.forEach(([big, lab, col], i) => {
      const x = L + i * (cw3 + 0.3);
      s.addText(big, { x, y: 1.9, w: 0.75, h: 0.8, fontSize: 44, bold: true, color: col, margin: 0, isTextBox: true, valign: "middle" });
      s.addText(lab, { x: x + 0.8, y: 1.9, w: cw3 - 0.8, h: 0.8, fontSize: 13, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    });
    // the grid: brand -> team
    const grid = [
      ["Stripe", "Mercedes-AMG Petronas", "comp"], ["Airwallex", "McLaren", "comp"],
      ["Mastercard", "McLaren", "scheme"], ["Visa", "Visa Cash App Racing Bulls", "scheme"], ["adyen", "Max Verstappen or Alpine", "adyen"],
    ];
    const tw = (CW - 4 * 0.25) / 5, ty = 2.95, th = 3.05;
    const arrowNavy = await icon("FiArrowDown", "8F97A3"), arrowGreen = await icon("FiArrowDown", "0ABF53");
    for (const [i, [brand, team, kind]] of grid.entries()) {
      const x = L + i * (tw + 0.25);
      const isA = kind === "adyen";
      if (isA) {
        s.addShape(S.ROUNDED_RECTANGLE, { x, y: ty, w: tw, h: th, rectRadius: 0.08, fill: { color: C.accent6 },
          line: { color: C.accent1, width: 1.5, dashType: "dash" }, objectName: "Adyen seat" });
      } else card(s, x, ty, tw, th);
      const tag = { comp: "COMPETITOR", scheme: "CARD SCHEME", adyen: "NOT YET IN F1" }[kind];
      const tagFill = kind === "comp" ? C.text1 : kind === "scheme" ? C.background1 : C.accent1;
      const tagText = kind === "comp" ? C.background1 : kind === "scheme" ? C.accent2 : C.text1;
      s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.2, y: ty + 0.22, w: tw - 0.4, h: 0.3, rectRadius: 0.15, fill: { color: tagFill },
        line: { color: kind === "scheme" ? C.accent1 : tagFill, width: 1 } });
      s.addText(tag, { x: x + 0.2, y: ty + 0.22, w: tw - 0.4, h: 0.3, fontSize: 8.5, bold: true, color: tagText, align: "center", valign: "middle",
        charSpacing: 1, margin: 0, isTextBox: true });
      if (isA) s.addImage({ path: A("adyen_green.png"), x: x + (tw - 1.25) / 2, y: ty + 0.75, w: 1.25, h: 0.4, altText: "Adyen logo" });
      else s.addText(brand, { x: x + 0.15, y: ty + 0.68, w: tw - 0.3, h: 0.55, fontSize: 22, bold: true, color: C.text1, align: "center",
        valign: "middle", margin: 0, isTextBox: true });
      s.addImage({ data: isA ? arrowGreen : arrowNavy, x: x + tw / 2 - 0.2, y: ty + 1.35, w: 0.4, h: 0.4 });
      s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.2, y: ty + 1.9, w: tw - 0.4, h: 0.9, rectRadius: 0.06,
        fill: { color: isA ? C.background1 : kind === "comp" ? C.text1 : C.accent5 }, line: { color: isA ? C.accent1 : C.text1, width: isA ? 1 : 0 } });
      s.addText([{ text: isA ? "ROUTE IN" : "F1 TEAM", options: { fontSize: 8.5, bold: true, color: isA ? C.accent2 : C.accent1, charSpacing: 1, breakLine: true } },
        { text: team, options: { fontSize: 12.5, bold: true, color: isA ? C.text1 : C.background1 } }],
      { x: x + 0.3, y: ty + 1.9, w: tw - 0.6, h: 0.9, align: "center", valign: "middle", margin: 0, isTextBox: true });
    }
    soWhat(s, "competitors are in, and schemes **co-exist with platforms** at McLaren: Adyen's seat is open.", 6.2);
  }

  // Competitors across sport
  {
    const s = content("CONTENT", SECTIONS[2], "03 Adyen in F1 · Competitors in sport",
      t("Adyen's competitors are buying into sport, but **only two have committed to F1**"),
      "Source: SPORTFIVE BI competitor scan (not exhaustive). Property types vary; no equivalence of rights, fees or exclusivity implied.",
      "Counts by column: F1 2, football 11, US leagues & college 12, other sport & venues 7 (32 properties in total).");
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
    soWhat(s, "competitor money is spread across football and US leagues. In F1, **only Stripe and Airwallex are in**: the category is open.", 6.22);
  }

  // Airwallex x McLaren benchmark
  {
    const s = content("CONTENT", SECTIONS[2], "03 Adyen in F1 · The benchmark",
      t("The model to beat: Airwallex × McLaren, **integration not a logo**"),
      "Source: SPORTFIVE (team deck: competitor scan, credentials, McLaren Racing and Airwallex case study).",
      "The benchmark Adyen's brief sets: a payments brand inside the team's business.");
    await photo(s, "airwallex_carbon.jpg", L, 2.0, 4.55, 4.6, "Airwallex branding on McLaren carbon fibre");
    const x = 5.55, w = R - x;
    label(s, "What Airwallex did", x, 2.0, w);
    const did = [
      "Put its product to work for McLaren: automated cross-border supplier payments, live in 14 days.",
      "Showcased its payment solutions to enterprises worldwide through the partnership.",
      "Built a B2B sports portfolio: McLaren, Arsenal FC, San Francisco Giants, Essendon FC.",
    ];
    did.forEach((d, i) => {
      const y = 2.35 + i * 0.62;
      s.addShape(S.OVAL, { x, y: y + 0.02, w: 0.32, h: 0.32, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
      s.addText(String(i + 1), { x, y: y + 0.02, w: 0.32, h: 0.32, fontSize: 11, bold: true, color: C.background1, align: "center",
        valign: "middle", margin: 0, isTextBox: true });
      s.addText(d, { x: x + 0.5, y, w: w - 0.5, h: 0.55, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
    });
    const res = [["14 days", "to go live"], ["90%", "of payments in hours"], ["110+", "countries, local rails"]];
    const rw = (w - 0.4) / 3;
    res.forEach(([big, lab], i) => {
      const rx = x + i * (rw + 0.2);
      card(s, rx, 4.3, rw, 1.0, C.text1);
      s.addText([{ text: big, options: { bold: true, color: C.accent1, fontSize: 20, breakLine: true } }, { text: lab, options: { color: C.accent4, fontSize: 10.5 } }],
        { x: rx + 0.2, y: 4.3, w: rw - 0.4, h: 1.0, margin: 0, isTextBox: true, valign: "middle" });
    });
    card(s, x, 5.5, w, 1.1, C.accent6, "Lessons");
    s.addText([{ text: "For Adyen  ", options: { bold: true, color: C.accent2 } },
      { text: "lead with where Adyen sits in the partner's business, show a clear line to revenue, and put hospitality at the centre.", options: { color: C.text1 } }],
    { x: x + 0.3, y: 5.5, w: w - 0.6, h: 1.1, fontSize: 13, margin: 0, valign: "middle", isTextBox: true });
  }

  // SPORTFIVE credentials (team deck slide 24)
  {
    const s = content("CONTENT", SECTIONS[2], "03 Adyen in F1 · SPORTFIVE credentials",
      t("This is what we've done: **Airwallex × McLaren**, powering performance"),
      "Source: SPORTFIVE. Images: McLaren Racing and Airwallex.",
      "SPORTFIVE's flagship F1 payments credential: we showcased Airwallex's payment solutions to enterprises worldwide through McLaren.");
    await fit(s, "mclaren_airwallex_logos.png", L, 1.95, 2.3, 1.3, "McLaren and Airwallex logos");
    s.addText("Showcased Airwallex's payment service solutions to a wide variety of enterprises on a global scale.",
      { x: L + 2.55, y: 2.0, w: 4.05, h: 1.2, fontSize: 15, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    const iw = (6.6 - 0.4) / 3;
    const imgs = [["airwallex_carbon.jpg", "Airwallex on McLaren carbon fibre"], ["airwallex_drivers.jpg", "McLaren drivers, Airwallex partner content"],
      ["airwallex_install.jpg", "Airwallex installation with McLaren driver"]];
    for (const [i, [f, alt]] of imgs.entries()) await photo(s, f, L + i * (iw + 0.2), 3.55, iw, 3.05, alt);
    const x = 7.55, w = R - x;
    card(s, x, 1.95, w, 4.65, C.text1, "Scope card");
    label(s, "Our scope of advisory and execution", x + 0.35, 2.2, w - 0.7, C.accent1);
    const scope = ["Diagnosed FinTech enterprise awareness gap", "Mapped F1 B2B opportunity landscape", "Benchmarked fintech differentiation positioning",
      "Built B2B partnership evaluation model", "Modelled investment scenario trade-offs", "Engineered enterprise-focused rights portfolio",
      "Structured deal for network access", "Enabled board-level partnership decision"];
    const check = await icon("FiCheck", "0ABF53");
    scope.forEach((it, i) => {
      const y = 2.65 + i * 0.48;
      s.addImage({ data: check, x: x + 0.35, y: y + 0.05, w: 0.24, h: 0.24 });
      s.addText(it, { x: x + 0.75, y, w: w - 1.0, h: 0.36, fontSize: 12, color: C.background1, margin: 0, isTextBox: true, valign: "middle" });
    });
  }

  // Proof of concept (team deck slide 25)
  {
    const s = content("CONTENT", SECTIONS[2], "03 Adyen in F1 · Proof of concept",
      t("How Airwallex **optimised McLaren's financial operations**"),
      "Source: McLaren Racing modernises cross-border payments with Airwallex (Airwallex case study), as compiled by SPORTFIVE.",
      "Challenge: 24 race locations, ~30 manual international payments per run, high FX and transfer fees, 2–5 day settlement via SWIFT; the cost cap makes efficiency matter. Solution: implemented in 14 days; batch payouts, approval workflows, faster cross-border transfers; suppliers paid in local currencies; integrated with banking and accounting.");
    await photo(s, "mclaren_team.jpg", L, 1.95, 4.2, 4.1, "McLaren team celebrating");
    const x1 = 5.1, w1 = 3.3;
    label(s, "The challenge", x1, 1.95, w1, C.accent2);
    s.addText("24 race locations. ~30 manual international payments per run. High FX fees, 2–5 day settlement, under a cost cap.",
      { x: x1, y: 2.25, w: w1, h: 1.45, fontSize: 12.5, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    label(s, "The solution", x1, 3.85, w1, C.accent2);
    s.addText("Live in 14 days: automated batch payouts and approvals, suppliers paid in local currencies, integrated with banking and accounting.",
      { x: x1, y: 4.15, w: w1, h: 1.6, fontSize: 12.5, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    const x = 8.7, w = R - x, tw = (w - 0.2) / 2, th = 1.25;
    const tiles = [["0.5 day", "saved per month"], ["£4,000+", "saved a year on fees"], ["110+", "countries, local rails"], ["65%", "of payments instant"]];
    tiles.forEach(([big, lab], i) => {
      const tx = x + (i % 2) * (tw + 0.2), ty = 1.95 + Math.floor(i / 2) * (th + 0.2);
      card(s, tx, ty, tw, th, i === 3 ? C.text1 : C.background2);
      s.addText(big, { x: tx + 0.2, y: ty + 0.15, w: tw - 0.4, h: 0.5, fontSize: 22, bold: true, color: i === 3 ? C.accent1 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: tx + 0.2, y: ty + 0.7, w: tw - 0.4, h: 0.45, fontSize: 11, color: i === 3 ? C.accent4 : C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    card(s, x, 4.85, w, 1.2, C.accent6);
    s.addText([{ text: "90%  ", options: { bold: true, color: C.accent2, fontSize: 24 } }, { text: "of payments arrive within hours", options: { color: C.text1, fontSize: 12 } }],
      { x: x + 0.2, y: 4.85, w: w - 0.4, h: 1.2, margin: 0, isTextBox: true, valign: "middle" });
    soWhat(s, "lower payment costs and faster cash: **efficiencies McLaren reinvests in racing performance**.", 6.2);
  }

  // Business integration (filled)
  {
    const s = content("CONTENT", SECTIONS[2], "03 Adyen in F1 · Business integration",
      t("Where Adyen sits **inside the partner's business**"),
      "Source: Adyen ('Racing | Unified Payments' value chain); Alpine Provisional Rights Overview 2027–2029; Max Verstappen × Adyen rights package.",
      "Integration first, not a logo deal. Top: Adyen's racing value chain, one platform from fan to business bank account. Each step shows what it means on the Alpine and Max routes.");
    await fit(s, "adyen_value_chain.png", L, 1.85, 7.4, 1.9, "Adyen unified commerce value chain, from fan to business bank account");
    const tx = 8.35, tw2 = R - tx;
    s.addText([{ text: "One platform, end to end", options: { bold: true, color: C.text1, fontSize: 15, breakLine: true } },
      { text: "Gateway, risk, authentication, processing, acquiring and reconciliation, online and in person.", options: { color: C.text2, fontSize: 12 } }],
    { x: tx, y: 2.05, w: tw2, h: 1.6, margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 4 });
    const steps = [
      ["FiCreditCard", "Power", "Adyen runs the partner's payments.", "Alpine: team ecommerce store. Max: Verstappen Travel tickets and trailers."],
      ["FiBarChart2", "Prove", "Live data becomes a client case study.", "KPIs: checkout completion, payment performance, conversion."],
      ["FiUsers", "Host", "Hospitality at the centre.", "Alpine: 56 Paddock Club tickets a year. Max: garage tours, track day."],
      ["FiShare2", "Connect", "The partner network becomes pipeline.", "Alpine: 42 Team partners, Partner Forum. Max: the Verstappen ecosystem."],
    ];
    const sw = (CW - 0.9) / 4, y = 3.92, h = 2.15;
    for (const [i, [ic, name, body, detail]] of steps.entries()) {
      const x = L + i * (sw + 0.3);
      card(s, x, y, sw, h);
      await iconDot(s, ic, x + 0.22, y + 0.18, 0.42);
      s.addText(`${i + 1}  ${name}`, { x: x + 0.75, y: y + 0.18, w: sw - 0.95, h: 0.42, fontSize: 15, bold: true, color: C.text1, margin: 0,
        isTextBox: true, valign: "middle" });
      s.addText(body, { x: x + 0.22, y: y + 0.68, w: sw - 0.44, h: 0.4, fontSize: 11.5, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });
      s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.15, y: y + 1.12, w: sw - 0.3, h: 0.88, rectRadius: 0.06, fill: { color: C.accent6 }, line: { color: C.accent6, width: 0 } });
      s.addText(detail, { x: x + 0.27, y: y + 1.12, w: sw - 0.54, h: 0.88, fontSize: 10.5, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
    }
    soWhat(s, "**integration first, not a logo deal**: every route is judged on how deeply Adyen sits in the partner's commerce.", 6.2);
  }

  // ROI
  {
    const s = content("CONTENT", SECTIONS[2], "03 Adyen in F1 · The return",
      t("The return: F1 **sources, accelerates, retains and proves** enterprise revenue"),
      "Source: SPORTFIVE partner analysis (team deck); HPE × Mercedes and Komatsu × Williams case material; Alpine Provisional Rights Overview 2027–2029; Adyen RSC Anderlecht case study.",
      "Every number is a proof point from a named source, not a forecast for Adyen. 42 Alpine partners and $369B Alpine partner revenue: SPORTFIVE team partner analysis (team deck slides 15-16; figures flagged as being re-checked by GF). $300M+: Antonio Neri, CEO HPE, 'From race activations alone, we've accelerated over $300M in revenue opportunity' (team deck slide 23). $100M+: Komatsu × Williams (team deck slide 23). 56 Paddock Club tickets: Alpine proposal (24+16+8+8). +36.6%: Adyen case study 'RSC Anderlecht increased F&B revenue by 36.6%'.");
    const levers = [
      ["FiSearch", "Source", "New deals", "42", "partners in Alpine's network (SPORTFIVE partner analysis)",
        "Team introductions and the Partner Forum. Alpine's partners: $369B combined revenue (SPORTFIVE)."],
      ["FiFastForward", "Accelerate", "Existing pipeline", "$300M+", "revenue opportunity HPE accelerated from race activations (HPE × Mercedes)",
        "Hosting decision-makers at races moves deals. Komatsu × Williams: $100M+ orders received at races."],
      ["FiRepeat", "Retain", "Priority accounts", "56", "Paddock Club tickets a year in Alpine's offer (Alpine proposal)",
        "C-level hosting in the Adyen Commerce Club keeps and grows priority accounts."],
      ["FiAward", "Prove", "Reusable case studies", "+36.6%", "F&B revenue at RSC Anderlecht with Adyen (Adyen case study)",
        "A live integration with the team becomes a flagship enterprise case study."],
    ];
    const cw = (CW - 0.9) / 4, y = 1.95, h = 3.95;
    for (const [i, [ic, verb, what, big, bigLab, body]] of levers.entries()) {
      const x = L + i * (cw + 0.3);
      card(s, x, y, cw, h, i % 2 === 0 ? C.background2 : C.background2);
      s.addShape(S.ROUNDED_RECTANGLE, { x, y, w: cw, h: 0.95, rectRadius: 0.08, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
      s.addShape(S.RECTANGLE, { x, y: y + 0.6, w: cw, h: 0.35, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
      await iconDot(s, ic, x + 0.22, y + 0.2, 0.55);
      s.addText([{ text: `${i + 1}  ${verb}`, options: { bold: true, color: C.background1, fontSize: 16, breakLine: true } },
        { text: what, options: { color: C.accent1, fontSize: 11, bold: true } }],
      { x: x + 0.9, y, w: cw - 1.05, h: 0.95, margin: 0, isTextBox: true, valign: "middle" });
      s.addText(big, { x: x + 0.25, y: y + 1.15, w: cw - 0.5, h: 0.65, fontSize: 32, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(bigLab, { x: x + 0.25, y: y + 1.85, w: cw - 0.5, h: 0.8, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
      s.addShape(S.LINE, { x: x + 0.25, y: y + 2.7, w: cw - 0.5, h: 0, line: { color: C.accent4, width: 0.75 } });
      s.addText(body, { x: x + 0.25, y: y + 2.8, w: cw - 0.5, h: 1.05, fontSize: 11, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    }
    card(s, L, 6.08, CW, 0.62, C.text1, "KPI strip");
    s.addText([{ text: "Track  ", options: { bold: true, color: C.accent1 } },
      { text: "pipeline sourced  ·  deals accelerated  ·  priority accounts retained and grown  ·  payment volume processed  ·  case studies published",
        options: { color: C.background1 } }],
    { x: L + 0.3, y: 6.08, w: CW - 0.6, h: 0.62, fontSize: 12.5, margin: 0, isTextBox: true, valign: "middle" });
  }

  // ================================================================ 04 The routes
  pres.addSection({ title: SECTIONS[3] });
  await divider(4, "The routes", "Two routes in to start with: Max Verstappen and Alpine F1 Team", "max_orange_army.jpg",
    "Section 4. Each route uses the same three slides: overview, business opportunity, rights. Photo: Orange Army (Verstappen proposal).");

  // Routes at a glance
  {
    const s = content("CONTENT", SECTIONS[3], "04 The routes · Overview",
      t("Two routes in to start, **then expand across the grid**"),
      "Source: Max Verstappen × Adyen proposal (Oct 2026, for discussion); Alpine F1 Team Provisional Rights Overview 2027–2029.",
      "Alpine and Max come from the conversations already under way. The aim is buy-in to F1 first; the wider grid (Ferrari is in the back-pocket slide) follows. Max's fee has not been quoted.");
    const cw = (CW - 0.6) / 3;
    const routes = [
      { n: 1, type: "Driver", name: "Max Verstappen", img: "max_banner.jpg", fields: [
        ["The opportunity", "Official ambassador; Adyen powers the Verstappen business ecosystem"],
        ["Where Adyen sits", "Verstappen Travel tickets and trailers; Pro Simulation booking"],
        ["Investment", "Fee not yet quoted"], ["Term and status", "2027–2030, non-exclusive; for discussion"]] },
      { n: 2, type: "Team", name: "Alpine F1 Team", img: "alpine_engine.jpg", fields: [
        ["The opportunity", "Exclusive Financial Technology Platform Partner, global"],
        ["Where Adyen sits", "Powers the Team's new ecommerce platform, then hospitality and network"],
        ["Investment", "£10.0M in 2027, +5% a year (£31.5M over 3 years)"], ["Term and status", "2027–2029; provisional, subject to contract"]] },
    ];
    for (const [i, r] of routes.entries()) {
      const x = L + i * (cw + 0.3), y = 2.0;
      card(s, x, y, cw, 4.75);
      await photo(s, r.img, x + 0.25, y + 0.25, cw - 0.5, 1.0, r.name);
      label(s, `Route ${r.n} · ${r.type}`, x + 0.3, y + 1.4, cw - 0.6, C.accent2);
      s.addText(r.name, { x: x + 0.3, y: y + 1.66, w: cw - 0.6, h: 0.42, fontSize: 19, bold: true, color: C.text1, margin: 0, isTextBox: true });
      r.fields.forEach(([f, v], k) => {
        const fy = y + 2.2 + k * 0.63;
        s.addText([{ text: f, options: { bold: true, color: C.text1, breakLine: true } }, { text: v, options: { color: C.text2 } }],
          { x: x + 0.3, y: fy, w: cw - 0.6, h: 0.6, fontSize: 10.5, margin: 0, isTextBox: true, valign: "top" });
      });
    }
    // the plan: buy-in first, then expand
    const x = L + 2 * (cw + 0.3), y = 2.0;
    card(s, x, y, cw, 4.75, C.text1, "Plan card");
    label(s, "The plan", x + 0.3, y + 0.3, cw - 0.6, C.accent1);
    const phases = [["1", "Start", "Commit to F1 through a route with a proposal on the table: Max, Alpine, or both."],
      ["2", "Prove", "Payments live inside the partner's business; hospitality and network at work."],
      ["3", "Expand", "Build across the grid from a proven start: more teams, races and markets."]];
    phases.forEach(([n, head, body], k) => {
      const py = y + 0.8 + k * 1.3;
      s.addShape(S.OVAL, { x: x + 0.3, y: py, w: 0.45, h: 0.45, fill: { color: k === 0 ? C.accent1 : C.accent5 }, line: { color: k === 0 ? C.accent1 : C.accent5, width: 0 } });
      s.addText(n, { x: x + 0.3, y: py, w: 0.45, h: 0.45, fontSize: 13, bold: true, color: k === 0 ? C.text1 : C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
      s.addText([{ text: head, options: { bold: true, color: C.background1, fontSize: 15, breakLine: true } }, { text: body, options: { color: C.accent4, fontSize: 11 } }],
        { x: x + 0.95, y: py - 0.03, w: cw - 1.2, h: 1.15, margin: 0, isTextBox: true, valign: "top" });
    });
  }

  // ---------- Route 1: Max Verstappen (Verstappen_Adyen_Oct2026 proposal; team deck slides 28-30)
  {
    const s = content("CONTENT_PHOTO", SECTIONS[3], "04 The routes · Route 1 · Max Verstappen",
      t("Max Verstappen: **F1's most popular driver**, and a business ecosystem"),
      "Source: Max Verstappen × Adyen proposal (October 2026); Nielsen Sports as cited. Visual: Max's team, logo placement for illustration.",
      "Four-time World Champion (2021–2024); 71 Grand Prix wins, 48 poles, 131 podiums. Nielsen Sports research names him the most popular driver on the grid. Social: Instagram 19M, X 4.6M, Facebook 3M, YouTube 1M; Verstappen.com channels add Instagram 2M, Threads 800K, TikTok 730K, X 300K.");
    await photo(s, "max_adyen_cap.jpg", 0, 0, 4.85, H, "Max Verstappen in an Adyen-branded GT3 cap (mock-up by Max Verstappen's team)");
    s.addShape(S.RECTANGLE, { x: 0, y: H - 1.15, w: 4.85, h: 1.15, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
    await fit(s, "max_adyen_lockup.jpg", 0.25, H - 1.1, 4.35, 1.05, "Max Verstappen, Adyen and Verstappen Racing logos");
    const x = 5.35, w = R - x;
    s.addText("Two Dutch innovators. Max has built one of sport's most successful personal brands; Adyen one of the world's leading financial technology platforms. Adyen becomes the platform behind the Verstappen ecosystem: racing, travel, merchandise and experiences.",
      { x, y: 1.95, w, h: 1.2, fontSize: 13, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    const stats = [["4×", "F1 World Champion, 2021–2024"], ["71", "Grand Prix wins"], ["19M", "Instagram followers"], ["#1", "most popular driver (Nielsen Sports)"]];
    const tw = (w - 0.6) / 4;
    stats.forEach(([big, lab], i) => {
      const tx = x + i * (tw + 0.2);
      card(s, tx, 3.3, tw, 1.35, i === 0 ? C.text1 : C.background2);
      s.addText(big, { x: tx + 0.2, y: 3.4, w: tw - 0.4, h: 0.6, fontSize: 30, bold: true, color: i === 0 ? C.accent1 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: tx + 0.2, y: 4.02, w: tw - 0.4, h: 0.55, fontSize: 10.5, color: i === 0 ? C.accent4 : C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    label(s, "The Verstappen.com ecosystem", x, 4.9, w);
    const biz = ["Shop", "Travel", "GT3 Racing", "Rally", "Sim Racing", "Pro Simulation", "News"];
    biz.forEach((b, i) => {
      const bw = (w - 0.12 * 6) / 7, bx = x + i * (bw + 0.12);
      s.addShape(S.ROUNDED_RECTANGLE, { x: bx, y: 5.2, w: bw, h: 0.42, rectRadius: 0.21, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
      s.addText(b, { x: bx, y: 5.2, w: bw, h: 0.42, fontSize: 10.5, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    });
    label(s, "Top markets by followers", x, 5.9, w);
    ["USA", "Brazil", "Netherlands", "Mexico", "UK", "Germany"].forEach((m, i) => {
      const mw = (w - 0.12 * 5) / 6, mx = x + i * (mw + 0.12);
      s.addShape(S.ROUNDED_RECTANGLE, { x: mx, y: 6.2, w: mw, h: 0.4, rectRadius: 0.2, fill: { color: C.accent6 }, line: { color: C.accent6, width: 0 } });
      s.addText(m, { x: mx, y: 6.2, w: mw, h: 0.4, fontSize: 11, bold: true, color: C.accent2, align: "center", valign: "middle", margin: 0, isTextBox: true });
    });
  }
  {
    const s = content("CONTENT", SECTIONS[3], "04 The routes · Route 1 · Business opportunity",
      t("Max is a business ecosystem: **Verstappen Travel is the most direct fit**"),
      "Source: SPORTFIVE assessment of the Verstappen business ecosystem (team deck); Max Verstappen × Adyen proposal (mock-ups: logo placement for illustration only).",
      "Powering a high-performance ecosystem. The online store is out of reach while Fanatics holds the exclusive deal. Mock-ups from Max's proposal: Orange Army app and MV Official Tickets shop powered by Adyen.");
    const vfill = { yes: C.accent6, no: C.background2, maybe: C.background1 };
    const rows = [[hc("Max's business", { fontSize: 10 }), hc("Adyen products", { fontSize: 10 }), hc("What it does", { fontSize: 10 }), hc("Can Adyen run it?", { fontSize: 10 })],
      ...MAX_BUSINESS.map(([biz, prod, what, can, v]) => {
        const i = can.indexOf(" ");
        const first = can.split(/(?<=[.,])\s/)[0];
        return [
          { text: biz, options: { bold: true, color: C.text1, fontSize: 9.5, valign: "middle" } },
          prod ? { text: prod, options: { color: C.text1, fontSize: 9.5, valign: "middle" } }
            : { text: "To define with Adyen", options: { italic: true, color: C.accent3, fontSize: 9.5, valign: "middle" } },
          { text: what, options: { color: C.text2, fontSize: 9.5, valign: "middle" } },
          { text: [{ text: first + " ", options: { bold: true, color: v === "yes" ? C.accent2 : C.text1 } },
            { text: can.slice(first.length).trim(), options: { color: C.text2 } }], options: { fontSize: 9.5, valign: "middle", fill: { color: vfill[v] } } },
        ];
      })];
    s.addTable(rows, { x: L, y: 1.95, w: 8.45, colW: [2.3, 1.45, 2.3, 2.4], rowH: [0.36, ...MAX_BUSINESS.map(() => 0.555)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.07, 0.03, 0.07], objectName: "Max business table" });
    const x = 9.3, w = R - x, ih = 2.1;
    await photo(s, "max_mock_tickets.jpg", x, 1.95, w, ih, "MV Official Tickets shop, powered by Adyen (mock-up)");
    s.addText("MV Official Tickets shop, powered by Adyen", { x, y: 1.95 + ih + 0.05, w, h: 0.25, fontSize: 9.5, color: C.accent3, margin: 0, isTextBox: true });
    await photo(s, "max_mock_app.jpg", x, 4.45, w, ih, "Orange Army app, powered by Adyen (mock-up)");
    s.addText("Orange Army app, powered by Adyen", { x, y: 4.45 + ih + 0.05, w, h: 0.25, fontSize: 9.5, color: C.accent3, margin: 0, isTextBox: true });
  }
  {
    const s = content("CONTENT", SECTIONS[3], "04 The routes · Route 1 · Rights package",
      t("Rights package: **Max Verstappen × Adyen**"),
      "Source: Max Verstappen × Adyen proposal (October 2026), for discussion purposes. Mock-ups: logo branding for illustration only.",
      "Transcribed from Max's proposal. The GT3 car position reads 'to discuss (not full car)'. Paddock Club hospitality is a SPORTFIVE addition: Max's own package excludes Red Bull assets and hospitality, so confirm how it is delivered.");
    const mocks = [["max_mock_cap.jpg", "GT3 driver cap"], ["max_mock_helmet.jpg", "GT3 helmet"], ["max_mock_gt3.jpg", "GT3 car livery"]];
    const mw = (CW - 0.5) / 3;
    for (const [i, [f, alt]] of mocks.entries()) await photo(s, f, L + i * (mw + 0.25), 1.9, mw, 1.65, `Adyen ${alt} (mock-up)`);
    const cols = [
      [["h", "Duration: 2027–2030 (3 years)"], ["h", "Ambassador role"],
        ["b", "Max as official ambassador"],
        ["b", "1 full day (6 hours) of Max's time: ad campaign, social, press"],
        ["b", "3 × 15-minute paddock meet-and-greets, each with 3 VIP guests"],
        ["b", "Non-exclusive IP rights (personal and Verstappen Racing): digital, TV, print, out of home"]],
      [["h", "Hospitality"], ["b", "F1 garage tour for 2 VIP guests"], ["b", "Private track day for stakeholders"],
        ["b", "Paddock Club at selected races (SPORTFIVE addition, to confirm)"],
        ["h", "Adyen business integration"],
        ["b", "Verstappen Travel: Orange Army grandstand ticketing, Spa and Austria GPs 2027 (to discuss)"],
        ["b", "Trailer and goodie-bag branding; joint B2C ticketing in GTWC, e.g. 24 Hours of Spa"],
        ["b", "Verstappen Pro Simulation: booking payment system"]],
      [["h", "Branding: GT3, Rally, Sim Racing"],
        ["b", "Helmets: Max's private helmet and all Verstappen Racing drivers (chin)"],
        ["b", "Mercedes GT3 2027 car and garage (to discuss)"],
        ["b", "Race suit and underwear top (chest, sleeves); cool vest; gloves"],
        ["b", "Team wear, multiple items (chest)"],
        ["h", "Content"], ["b", "Max and Verstappen.com social channels (to discuss)"]],
    ];
    rightsColumns(s, cols, 3.75, 3.1, [L, L + 4.15, L + 8.3], [3.85, 3.85, 3.83], 10.5);
  }

  // ---------- Route 2: Alpine (Alpine Provisional Rights Overview 2027-2029)
  {
    const s = content("CONTENT", SECTIONS[3], "04 The routes · Route 2 · Alpine F1 Team",
      t("Alpine: **Performance in Every Transaction**, from checkout to chequered flag"),
      "Source: Alpine Formula One Team, Provisional Rights Overview 2027–2029 (not legally binding). Audience: GWI Core, Q3 2025–Q2 2026, all internet users.",
      "Alpine's objectives for Adyen: (1) prove the enterprise platform through a measurable ecommerce integration and a client-facing case study; (2) deepen relationships with priority customers through C-level hospitality and F1 experiences; (3) generate qualified new business through the Team's international partner network.");
    const lw = 6.15;
    s.addText("Every F1 result depends on thousands of processes working with speed, precision and resilience; Adyen does the same for enterprise commerce. As exclusive Financial Technology Platform Partner, Adyen powers Alpine's new ecommerce platform, then turns that proof into senior customer conversations and new business.",
      { x: L, y: 1.95, w: lw, h: 1.7, fontSize: 13, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    label(s, "Alpine fans vs. the average internet user", L, 3.85, lw);
    const aud = [["10.0M", "senior decision-makers", "2.22x"], ["23.6M", "business decision-makers", "1.88x"], ["5.6M", "company owners, founders", "1.98x"],
      ["4.5M", "technology early adopters", "3.02x"], ["24.3M", "Google Pay users", "1.83x"], ["7.2M", "Apple Pay users", "1.59x"]];
    const aw = (lw - 0.4) / 3, ah = 1.12;
    aud.forEach(([big, lab, idx], i) => {
      const ax = L + (i % 3) * (aw + 0.2), ay = 4.2 + Math.floor(i / 3) * (ah + 0.15);
      card(s, ax, ay, aw, ah);
      s.addText([{ text: big + " ", options: { fontSize: 19, bold: true, color: C.text1 } }, { text: idx, options: { fontSize: 11, bold: true, color: C.accent2 } }],
        { x: ax + 0.18, y: ay + 0.12, w: aw - 0.36, h: 0.45, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: ax + 0.18, y: ay + 0.6, w: aw - 0.36, h: 0.42, fontSize: 10.5, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
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
    const s = content("CONTENT", SECTIONS[3], "04 The routes · Route 2 · Business opportunity",
      t("Alpine: Adyen **powers the Team's commerce**, then turns that proof into relationships"),
      "Source: Alpine Formula One Team, Provisional Rights Overview 2027–2029: marketing framework and appendix.",
      "Four pillars: Power the experience (rows 1-2), Prove the performance (rows 3-4), Bring it to life (row 5), Accelerate relationships (rows 6-7). The Partner Forum facilitates introductions without guaranteeing procurement outcomes.");
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
    const s = content("CONTENT", SECTIONS[3], "04 The routes · Route 2 · Rights overview",
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
        ["kv", "Kit:", "driver and mechanics suit collar*; helmets chin; team kit collar*"],
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
        ["kv", "Paddock Club:", "56 tickets: 24 at selected races, 16 at Monaco, Singapore, Austin or Abu Dhabi, 8 at Miami, 8 at Las Vegas"],
        ["kv", "Also:", "grandstand tickets at partner rate; one-day paddock passes on request; 2 U.S. near-track dinners (15 guests)"],
        ["h", "Off-track experiences"],
        ["kv", "Enstone:", "2 VIP factory tours (12 guests) and 1 factory event (60 guests), at Alpine's cost"],
        ["kv", "Assets:", "showcar and Trak Racer simulators, 14 days' hire each at Adyen's cost"],
        ["kv", "Driving:", "1 motorsport driving day for 24 guests at Alpine's cost"],
        ["kv", "Network:", "introductions to Alpine's partners; 6 car-launch tickets"],
        ["h", "Merchandise"],
        ["b", "Polos and caps: 40 signed and 80 unsigned of each; 2 replica helmets, 50 mini helmets, 2 replica driver sets"]],
    ];
    rightsColumns(s, cols, 1.95, 4.9, [L, L + 4.15, L + 8.3], [3.85, 3.85, 3.83], 10.5);
  }

  // ================================================================ Next steps
  pres.addSection({ title: "Next steps" });
  {
    const s = content("CONTENT", "Next steps", "Investment and next steps",
      t("Investment and **next steps**"),
      "Source: Adyen budget guidance; GlobalData (average annual value of new F1 deals, 2025); Alpine Provisional Rights Overview 2027–2029.",
      "Budget guidance from Adyen: $10M a year is defensible, $20M needs a very strong case, and a $5-7M option shows how it works. Dashed line: average annual value of a new F1 deal in 2025 ($5.78M). Alpine's fee is in GBP and shown as quoted, not converted.");
    label(s, "Investment envelope per year (Adyen guidance)", L, 2.0, 7);
    const opts = [["Prove the model", "$5–7M", 7, 5, "Shows how it works"], ["Defensible core", "$10M", 10, null, "Defensible"],
      ["Flagship", "$20M", 20, null, "Needs a very strong case"]];
    const bx = L + 2.0, bw = 4.75, max = 20;
    opts.forEach(([name, val, hi, lo, note], i) => {
      const y = 2.45 + i * 1.0;
      s.addText(name, { x: L, y, w: 1.9, h: 0.42, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      s.addShape(S.RECTANGLE, { x: bx, y: y + 0.06, w: bw, h: 0.3, fill: { color: C.background2 }, line: { color: C.background2, width: 0 } });
      if (lo) s.addShape(S.RECTANGLE, { x: bx, y: y + 0.06, w: (bw * lo) / max, h: 0.3, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
      s.addShape(S.RECTANGLE, { x: bx + (lo ? (bw * lo) / max : 0), y: y + 0.06, w: (bw * (hi - (lo || 0))) / max, h: 0.3,
        fill: { color: lo ? C.accent6 : C.accent1 }, line: { color: C.accent1, width: lo ? 1 : 0 } });
      s.addText(val, { x: bx + (bw * hi) / max + 0.1, y, w: 0.9, h: 0.42, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      s.addText(note, { x: bx, y: y + 0.45, w: bw, h: 0.3, fontSize: 10.5, italic: true, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    const mx = bx + (bw * 5.78) / max;
    opts.forEach((_, i) => s.addShape(S.LINE, { x: mx, y: 2.45 + i * 1.0 - 0.02, w: 0, h: 0.46,
      line: { color: C.text1, width: 1.25, dashType: "dash" } }));
    s.addShape(S.LINE, { x: L, y: 5.5, w: 0.3, h: 0, line: { color: C.text1, width: 1.25, dashType: "dash" } });
    s.addText("Average annual value of a new F1 deal, 2025: $5.78M", { x: L + 0.4, y: 5.36, w: 5.5, h: 0.28, fontSize: 10.5,
      color: C.text2, margin: 0, isTextBox: true, valign: "middle" });
    card(s, L, 5.85, 7.3, 0.85, C.text1, "On the table");
    s.addText([{ text: "On the table   ", options: { bold: true, color: C.accent1 } },
      { text: "Alpine ", options: { bold: true, color: C.background1 } }, { text: "£10.0M in 2027, +5% a year.   ", options: { color: C.accent4 } },
      { text: "Max ", options: { bold: true, color: C.background1 } }, { text: "fee not yet quoted.", options: { color: C.accent4 } }],
    { x: L + 0.25, y: 5.85, w: 6.8, h: 0.85, fontSize: 12, margin: 0, isTextBox: true, valign: "middle" });

    const x = 8.3, w = R - x;
    label(s, "Next steps", x, 2.0, w);
    const steps = [["Chairman reviews the Max and Alpine routes", "Week of 9 November 2026"], ["Gather feedback", null],
      ["Explore or revisit the rights packages", null], ["Open a conversation with Ferrari, or not", null],
      ["Contract and integration plan", null], ["Launch", null]];
    s.addShape(S.LINE, { x: x + 0.14, y: 2.5, w: 0, h: 3.9, line: { color: C.accent4, width: 1.5 } });
    steps.forEach(([st, when], i) => {
      const y = 2.38 + i * 0.75;
      s.addShape(S.OVAL, { x, y, w: 0.28, h: 0.28, fill: { color: i === 0 ? C.accent1 : C.text1 }, line: { color: C.background1, width: 2 } });
      s.addText(String(i + 1), { x, y, w: 0.28, h: 0.28, fontSize: 9, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true });
      s.addText(when ? [{ text: st, options: { bold: true, color: C.text1, breakLine: true } }, { text: when, options: { color: C.accent2, bold: true, fontSize: 11 } }]
        : [{ text: st, options: { bold: true, color: C.text1 } }],
      { x: x + 0.5, y: y - 0.05, w: w - 0.5, h: 0.62, fontSize: 13, margin: 0, valign: "top", isTextBox: true });
    });
  }

  // Hidden: route assessment and KPI slide (kept for later)
  {
    const s = content("CONTENT", "Next steps", "Recommendation · Assessment",
      [{ text: "Why we recommend " }, { text: "[ADD: route]", options: { color: C.accent1 } }],
      "Source: SPORTFIVE assessment against Adyen's partnership brief; rights-holder proposals.",
      "Hidden for now. Evidence in each cell comes from the proposals. Rate each route ● strong, ◐ partial, ○ weak when the recommendation is made.");
    s.hidden = true;
    const crit = [...BRIEF_CRITERIA, "Fits the investment envelope", "Payments category available"];
    const ev = {
      max: ["Verstappen Travel ticketing and trailers fit directly; the store is held by Fanatics", "Grandstand ticketing (Spa, Austria 2027) and trackside merchandise",
        "Garage tour, track day, paddock meet-and-greets; Paddock Club to be added", "Max's personal business ecosystem; no team partner network",
        "Top follower markets: USA, Brazil, Netherlands, Mexico, UK, Germany", "Fee not yet quoted", "Non-exclusive ambassador rights"],
      alp: ["Powers agreed parts of the Team's new ecommerce platform", "Checkout, rewards and race-week venue payments; KPIs proposed",
        "56 Paddock Club tickets a year, Enstone events, near-track dinners", "Introductions to 42 Team partners; One Platform Partner Forum",
        "Global rights; races across all of Adyen's regions", "£10.0M in 2027, rising 5% a year", "Exclusive Financial Technology Platform category"],
    };
    const rate = { text: "[ ● ◐ ○ ]  ", options: { bold: true, color: C.accent3 } };
    const cell = (txt) => ({ text: [rate, { text: txt, options: { color: C.text1 } }], options: { fontSize: 10, valign: "middle" } });
    const rows = [[hc("Criterion", { fontSize: 12 }), ...ROUTE_NAMES.map((r) => hc(r, { align: "center", fontSize: 12 }))],
      ...crit.map((c, i) => [
        { text: c, options: { color: C.text1, fontSize: 11.5, bold: true, valign: "middle", fill: { color: C.background2 } } },
        cell(ev.max[i]), cell(ev.alp[i]),
        { text: "No proposal yet", options: { italic: true, color: C.accent3, fontSize: 10, align: "center", valign: "middle" } },
      ])];
    s.addTable(rows, { x: L, y: 1.95, w: CW, colW: [3.13, 3.4, 3.4, 2.2], rowH: [0.42, ...crit.map(() => 0.5)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.1, 0.03, 0.1], objectName: "Assessment table" });
  }
  {
    const s = content("CONTENT", "Next steps", "Recommendation · Value",
      t("A clear line to **revenue and payment volume**"),
      "Source: Adyen case studies (FC Bayern, RSC Anderlecht); KPI targets [ADD].", "Hidden for now: KPI targets to be set with Adyen.");
    s.hidden = true;
    label(s, "How the partnership pays back", L, 2.0, 7);
    const kpis = [["FiDollarSign", "Payment volume processed"], ["FiTarget", "Qualified pipeline"], ["FiUsers", "C-level guests hosted"], ["FiFileText", "Case studies and new logos"]];
    const kw = (7.25 - 0.3) / 2, kh = 1.95;
    for (const [i, [ic, name]] of kpis.entries()) {
      const x = L + (i % 2) * (kw + 0.3), y = 2.35 + Math.floor(i / 2) * (kh + 0.25);
      card(s, x, y, kw, kh);
      await iconDot(s, ic, x + 0.3, y + 0.28, 0.46);
      s.addText(name, { x: x + 0.9, y: y + 0.28, w: kw - 1.1, h: 0.46, fontSize: 13, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      s.addText("[ADD]", { x: x + 0.3, y: y + 0.9, w: kw - 0.6, h: 0.55, fontSize: 28, color: C.accent3, margin: 0, isTextBox: true, valign: "top" });
    }
    const x = 8.2, w = R - x;
    const proof = [["+36.6%", "F&B revenue at RSC Anderlecht", "adyen_stadium.jpg"], ["1 platform", "for every FC Bayern payment", "adyen_fans.jpg"]];
    for (const [i, [big, head, img]] of proof.entries()) {
      const y = 2.35 + i * 2.2;
      await photo(s, img, x, y, w, 1.95, "Adyen in sport");
      s.addShape(S.RECTANGLE, { x, y, w, h: 1.95, fill: { color: C.text1, transparency: 18 }, line: { color: C.text1, width: 0 } });
      s.addText([{ text: big, options: { color: C.accent1, fontSize: 30, breakLine: true } }, { text: head, options: { bold: true, color: C.background1, fontSize: 12 } }],
        { x: x + 0.3, y: y + 0.2, w: w - 0.6, h: 1.5, margin: 0, isTextBox: true, valign: "top" });
    }
  }

  // ================================================================ Back pocket: the wider grid (Ferrari)
  pres.addSection({ title: "Back pocket" });
  {
    const s = content("CONTENT", "Back pocket", "Back pocket · The wider grid",
      t("Scuderia Ferrari: **the third-largest partner network** in F1"),
      "Source: SPORTFIVE partner network analysis (team deck); GWI (2026). Figures under review by the team.",
      "Back pocket: show only if the Chairman asks about the wider grid or other options. No Ferrari proposal yet. The Ferrari business-opportunity and rights slides are hidden until a proposal exists.");
    await photo(s, "f1_city.jpg", L, 1.95, 4.3, 4.7, "F1 car at speed");
    const x = L + 4.65, w = R - x;
    const stats = [["$705B", "combined revenue of Ferrari's partners: #3 of 11 teams"], ["40", "partners, half of them public companies"],
      ["1.80M", "Ferrari fans working in financial services: the largest of any team"], ["5", "financial-services partners already in the network"]];
    const tw = (w - 0.25) / 2, th = 1.35;
    stats.forEach(([big, lab], i) => {
      const tx = x + (i % 2) * (tw + 0.25), ty = 1.95 + Math.floor(i / 2) * (th + 0.2);
      card(s, tx, ty, tw, th);
      s.addText(big, { x: tx + 0.25, y: ty + 0.15, w: tw - 0.5, h: 0.6, fontSize: 30, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: tx + 0.25, y: ty + 0.78, w: tw - 0.5, h: 0.5, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    s.addText([{ text: "Top partners  ", options: { bold: true, color: C.text1 } }, { text: "Shell, IBM, HP", options: { color: C.text2 } }],
      { x, y: 4.95, w, h: 0.35, fontSize: 13, margin: 0, isTextBox: true, valign: "middle" });
    card(s, x, 5.45, w, 1.2, C.text1, "Status card");
    s.addText([{ text: "Status  ", options: { bold: true, color: C.accent1, fontSize: 13 } },
      { text: "Not yet explored. Once Adyen is committed to F1, Ferrari is a natural next conversation.", options: { color: C.background1, fontSize: 13 } }],
    { x: x + 0.3, y: 5.45, w: w - 0.6, h: 1.2, margin: 0, isTextBox: true, valign: "middle" });
  }
  {
    const s = content("CONTENT", "Back pocket", "Back pocket · Ferrari business opportunity",
      [{ text: "Ferrari: " }, { text: "[ADD: where Adyen sits in Ferrari's business]", options: { color: C.accent3, italic: true } }],
      "Source: [ADD]", "Hidden until a Ferrari proposal exists. Same columns as Max and Alpine.");
    s.hidden = true;
    const blank = () => ({ text: "[ADD]", options: { italic: true, color: C.accent3, fontSize: 11, valign: "middle" } });
    const rows = [[hc("Ferrari's business"), hc("Adyen products"), hc("What it does"), hc("Can Adyen run it?")],
      ...[0, 1, 2, 3, 4].map(() => [blank(), blank(), blank(), blank()])];
    s.addTable(rows, { x: L, y: 2.0, w: CW, colW: [3.2, 2.2, 3.15, 3.58], rowH: [0.4, 0.62, 0.62, 0.62, 0.62, 0.62],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.04, 0.1, 0.04, 0.1], objectName: "Ferrari business table" });
  }
  {
    const s = content("CONTENT", "Back pocket", "Back pocket · Ferrari rights package",
      [{ text: "Rights package: " }, { text: "Scuderia Ferrari × Adyen", options: { color: C.accent1 } }],
      "Source: [ADD: Ferrari proposal]", "Hidden: left blank until a Ferrari proposal exists.");
    s.hidden = true;
    const heads = [["Commercial terms", "Category, designation, term, fee, payment schedule"], ["Branding and IP", "Car, kit, team environment; IP rights"],
      ["Hospitality and experiences", "Paddock Club, factory, driving, merchandise"]];
    heads.forEach(([h, lab], i) => {
      const x = L + i * 4.15;
      label(s, h, x, 2.0, 3.85, C.accent2);
      ph(s, x, 2.35, 3.85, 4.3, lab, { size: 12, align: "left" });
    });
  }

  // ================================================================ Appendix
  pres.addSection({ title: "Appendix" });
  {
    const s = content("CONTENT", "Appendix", "Appendix", t("Sources and notes"), "Prepared by SPORTFIVE for Adyen. Data as supplied; not independently verified unless stated.",
      "Keep this slide: it answers 'where does that number come from?' in the room. Hidden slides: Ferrari business opportunity and rights (until a proposal exists), route assessment, KPI targets.");
    const src = [
      ["GWI", "Global F1 audience 2022–2026; F1 audience by Adyen office market; sport affinity indices; team fans working in financial services (2026); Alpine fan audience (GWI Core, Q3 2025–Q2 2026)."],
      ["GlobalData", "F1 sponsorship 2020–2025 (new deals only); brands involved in F1 and their combined revenue (2026)."],
      ["Kantar", "BrandZ 2026 Most Valuable Global Brands; Strong Brands Portfolio 2006–2026; IBM and American Express spotlights; Kantar × Google 2026."],
      ["SPORTFIVE", "Competitor scan (not exhaustive); team partner networks: revenue, market-cap tiers, sector mapping (estimates; being re-checked); F1 partner case studies; Airwallex × McLaren credentials."],
      ["Rights holders", "Alpine Formula One Team, Provisional Rights Overview 2027–2029 (not legally binding). Max Verstappen × Adyen proposal, October 2026 (for discussion)."],
      ["Adyen", "Office locations; FC Bayern and RSC Anderlecht case studies; partnership brief; 'Racing | Unified Payments' imagery and value chain."],
      ["Imagery", "Adyen; SPORTFIVE team deck; Max Verstappen proposal (Verstappen.com); Alpine F1 Team mock-ups. Mock-up logo placements are for illustration only."],
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
