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

const OUT = process.argv[2] || "Adyen x F1 - Chairman deck 5.pptx";
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
// storyline sections, shown as a tracker at the top right of every content slide
const TRACK = ["Why F1", "Hospitality", "Adyen in F1", "The routes", "Next steps"];

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
function content(master, section, track, eyebrow, title, source, notes) {
  const s = pres.addSlide({ masterName: master, sectionTitle: section });
  s.addText(eyebrow.toUpperCase(), { placeholder: "eyebrow" });
  if (track !== null && track !== undefined) {
    const runs = [];
    TRACK.forEach((name, i) => {
      if (i) runs.push({ text: "   ·   ", options: { color: C.accent4 } });
      runs.push({ text: name, options: { color: i === track ? C.accent2 : C.accent3, bold: i === track } });
    });
    s.addText(runs, { x: 7.6, y: 0.36, w: R - 7.6, h: 0.3, fontSize: 9, align: "right", valign: "middle", margin: 0, isTextBox: true,
      objectName: "Section tracker" });
  }
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
  ["Verstappen official app", "",
    "Currently free: news, stats, alerts, and a link to the shop. Adds one-tap purchase in the app for merchandise, grandstand tickets and experiences.",
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

// what Max's own proposal (Verstappen_Adyen_Oct2026) says for each business line
const MAX_PROPOSAL = [
  "Not part of the proposal: the store is run with Fanatics",
  "Orange Army grandstand ticketing, Spa and Austria GPs 2027 (to discuss); MV Official Tickets shop (mock-up)",
  "Branding on the trailers and Orange Army goodie bags",
  "Joint B2C ticketing in GTWC, e.g. 24 Hours of Spa (to discuss); GT3 car, helmet and race-wear branding",
  "Sim Racing branding: one of Max's personal racing pillars (GT3, Rally, Sim Racing)",
  "Booking payment system",
  "Not in the proposal",
  "Orange Army app powered by Adyen (mock-up)",
];
// team deck slides 16 and 17: total partners (Audi not covered) and FS&I partners, by team
const PARTNERS = { "Mercedes-AMG": 28, "McLaren": 54, "Ferrari": 40, "Aston Martin": 34, "Red Bull Racing": 32, "Alpine": 42,
  "Racing Bulls": 24, "Williams": 27, "Cadillac": 10, "Audi": null, "Haas": 22 };
const FSI = { "Mercedes-AMG": 3, "McLaren": 6, "Ferrari": 5, "Aston Martin": 4, "Red Bull Racing": 4, "Alpine": 4,
  "Racing Bulls": 2, "Williams": 6, "Cadillac": 1, "Audi": 3, "Haas": 2 };

const ROUTE_NAMES = ["Max Verstappen", "Alpine F1 Team", "Scuderia Ferrari"];

// ------------------------------------------------------------------ slides
// Deck 5: 27 visible slides, no dividers; the tracker at the top right shows the section.
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

  // Adyen's brief (team deck slide 2, plus payment integration)
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
    s.addNotes("Source: Briefing - Adyen x Premium Experiences (Adyen), sections 1–5 and 7, as summarised in the team deck (slide 2). Payment integration added at the user's request: Adyen wants its payment solutions shown working for teams or rights holders.");
  }

  // Hypothesis + how to judge F1 (team deck slide 3, plus the platform lens)
  {
    const s = content("CONTENT", "Introduction", null, "Our partnership hypothesis",
      t("An F1 partnership can build Adyen's global brand and deepen client relationships through **payments storytelling** and a **global hospitality programme**"),
      "Source: team deck (hypothesis); GlobalData (2026); GWI; Max Verstappen × Adyen proposal (Nielsen Sports); SPORTFIVE team partner analysis.",
      "The hypothesis is the team deck's (slide 3). The framing for the meeting: transaction volume is real but it is not the headline; the case is brand, audience, influence, hospitality, network and proof working together.");
    label(s, "How to judge F1", L, 2.32, 4);
    const lw = 3.85, y0 = 2.65, hh = 4.05;
    card(s, L, y0, lw, hh, C.background2, "Transaction lens");
    await iconDot(s, "FiCreditCard", L + 0.35, y0 + 0.3, 0.7, C.accent3);
    s.addText("The transaction lens", { x: L + 0.35, y: y0 + 1.15, w: lw - 0.7, h: 0.45, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText("Payment volume through a team's checkout, tickets and merchandise.", { x: L + 0.35, y: y0 + 1.7, w: lw - 0.7, h: 0.9,
      fontSize: 13, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
    s.addText("Real, and part of the case. On its own, it undersells F1.", { x: L + 0.35, y: y0 + 2.6, w: lw - 0.7, h: 0.9,
      fontSize: 13, bold: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    const x = L + lw + 0.3, w = R - x;
    card(s, x, y0, w, hh, C.text1, "Platform lens");
    label(s, "The platform lens: what F1 actually delivers", x + 0.35, y0 + 0.2, w - 0.7, C.accent1);
    const rows = [
      ["FiAward", "Brand", "50% of the world's most valuable brands are involved in F1"],
      ["FiUsers", "Audience", "#1 sport for all five audiences Adyen sells to"],
      ["FiStar", "Influence", "Max Verstappen: F1's most popular driver, 19M Instagram followers"],
      ["FiCoffee", "Hospitality", "24 race weekends a year to host clients and prospects"],
      ["FiShare2", "Network", "350+ global brands in team partner portfolios"],
      ["FiCheckCircle", "Proof", "Adyen's payments live inside a team's business: an enterprise case study"],
    ];
    for (const [i, [ic, head, body]] of rows.entries()) {
      const ry = y0 + 0.58 + i * 0.56;
      await iconDot(s, ic, x + 0.35, ry, 0.44);
      s.addText(head, { x: x + 1.0, y: ry, w: 1.6, h: 0.44, fontSize: 14, bold: true, color: C.background1, margin: 0, isTextBox: true, valign: "middle" });
      s.addText(body, { x: x + 2.6, y: ry, w: w - 2.9, h: 0.44, fontSize: 12.5, color: C.accent4, margin: 0, isTextBox: true, valign: "middle" });
    }
  }

  // Executive summary
  {
    const s = content("CONTENT", "Introduction", null, "Executive summary",
      t("F1 is a **global commercial engine**, and Adyen can power it"),
      "Source: GWI; GlobalData; Adyen; partner case studies; rights-holder proposals; SPORTFIVE analysis. See Sources and notes.",
      "The storyline in six steps, then the three routes. Each tile is one part of the deck.");
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
    label(s, "Three routes into F1", x + 0.3, y + 0.25, w - 0.6, C.accent1);
    const routes = [
      ["max_thumb.jpg", "Max Verstappen", "Adyen powers the Verstappen ecosystem: ticketing, trackside, simulation"],
      ["alpine_engine.jpg", "Alpine F1 Team", "Exclusive FinTech Platform Partner; Adyen powers the Team's ecommerce"],
      ["f1_city.jpg", "Scuderia Ferrari", "Third-largest partner network in F1; to explore"],
    ];
    for (const [i, [img, name, body]] of routes.entries()) {
      const ry = y + 0.68 + i * 1.02;
      await photo(s, img, x + 0.3, ry, 0.8, 0.8, name);
      s.addText([{ text: name, options: { bold: true, color: C.background1, fontSize: 14, breakLine: true } },
        { text: body, options: { color: C.accent4, fontSize: 10.5 } }],
      { x: x + 1.3, y: ry - 0.02, w: w - 1.55, h: 0.85, margin: 0, isTextBox: true, valign: "top" });
    }
    s.addShape(S.LINE, { x: x + 0.3, y: y + 3.78, w: w - 0.6, h: 0, line: { color: C.accent5, width: 0.75 } });
    s.addText([{ text: "Next  ", options: { bold: true, color: C.accent1 } }, { text: "Chairman review, w/c 9 November", options: { color: C.background1 } }],
      { x: x + 0.3, y: y + 3.85, w: w - 0.6, h: 0.35, fontSize: 11.5, margin: 0, isTextBox: true, valign: "middle" });
  }

  // ================================================================ 01 Why F1
  pres.addSection({ title: "Why F1" });
  // Growth
  {
    const s = content("CONTENT", "Why F1", 0, "Growth",
      t("F1 is growing in **audience and in commercial value**"),
      "Source: GWI (global audience, followers); GlobalData (new sponsorship deals only, excl. renewals). 2026 YTD: $1.91B across 139 deals, year incomplete.",
      "Audience: 478.0M (2022) to 625.3M (2026), +30.8%, +147.3M followers; +8.3% vs 2025.\nSponsorship: total value of NEW deals, not annual sponsorship revenue. $0.89B (2020) to $2.37B (2025), +165.3%. 125 new deals in 2025 (+28.9%). Average annual value $5.78M in 2025 (+161.5%); the 2020 figure of $2.21M is calculated from those two numbers.");
    const cards = [
      { x: L, head: "Global F1 audience", big: "+30.8%", sub: "2022–2026 · 147.3M additional followers", d: AUDIENCE,
        fmt: '0.0"M"', note: "625.3M followers in 2026, +8.3% vs 2025" },
      { x: L + CW / 2 + 0.15, head: "New F1 sponsorship deal value", big: "+165.3%", sub: "2020–2025 · new deals only, excludes renewals", d: DEALS,
        fmt: '"$"0.00"B"', note: "125 new deals in 2025 (+28.9%)" },
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
    soWhat(s, "brands are paying more to be in F1: the average new deal reached **$5.78M a year in 2025, up 161.5%**.");
  }

  // Business leader network (team deck slide 11)
  {
    const s = content("CONTENT", "Why F1", 0, "Business leader network",
      t("Half of the world's most valuable brands are **already in F1**"),
      "Source: GlobalData (2026).",
      "Team deck slide 11. 50% of the world's most valuable brands are involved in F1; the public brands in the F1 ecosystem have combined revenue of $10T, compared with the GDP of five of the seven largest economies.");
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

  // Brand value (team deck slides 38-39)
  {
    const s = content("CONTENT", "Why F1", 0, "Brand value",
      t("The strongest brands **outperform the market**, and many of them race in F1"),
      "Source: Kantar BrandZ 2026 (Top 100, Strong Brands Portfolio, brand spotlights); Kantar × Google 2026. F1 involvement marked by SPORTFIVE.",
      "Left: Kantar BrandZ 2026 Top 100, with the brands the team identified as involved in F1 boxed. IBM and American Express: the team's analysis is that both posted their biggest brand-value increase in the year they entered F1 partnerships.");
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

  // Audience (affinity + fans in financial services)
  {
    const s = content("CONTENT", "Why F1", 0, "Audience",
      t("F1 is the strongest sport for **every audience Adyen sells to**"),
      "Source: GWI. Affinity index across the five sports assessed. Fans in financial services: Global Web Index (2026), North America and Europe, average of 11 teams.",
      "Indices are not percentages. '31%' and '12% above the next-best sport' are calculated from the index values (237.9 vs 181.8; 166.6 vs 148.1). Fans working in financial services, index vs general population: Mercedes 172.9 (highest), Alpine 140.1, Ferrari 136.2 with 1.80M fans (largest pool); 11-team average 145.0. Full chart in the backup slides.");
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
      { x: L, y: 5.72, w: 8.35, h: 0.3, fontSize: 11, color: C.text2, margin: 0, isTextBox: true });
    const stats = [
      ["237.9", "Early tech adopters", "31% above the next-best sport", true],
      ["166.6", "Senior decision-makers", "12% above the next-best sport", false],
      ["145.0", "Fans working in financial services", "11-team average index. Alpine 140.1; Ferrari: 1.80M, the largest pool", false],
    ];
    stats.forEach(([big, head, body, dark], i) => {
      const x = 9.25, y = 2.0 + i * 1.4, w = R - 9.25, h = 1.27;
      card(s, x, y, w, h, dark ? C.text1 : C.background2);
      s.addText(big, { x: x + 0.25, y: y + 0.12, w: w - 0.5, h: 0.5, fontSize: 26, bold: true, color: dark ? C.accent1 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText([{ text: head, options: { bold: true, color: dark ? C.background1 : C.text1, breakLine: true } }, { text: body, options: { color: dark ? C.accent4 : C.text2 } }],
        { x: x + 0.25, y: y + 0.62, w: w - 0.5, h: 0.6, fontSize: 10.5, margin: 0, isTextBox: true, valign: "top" });
    });
    soWhat(s, "F1 leads on **every audience Adyen needs**, from enterprise buyers to the consumers adopting new ways to pay.", 6.15, L, 8.35);
  }

  // Footprint (offices and races, Adyen markets)
  {
    const s = content("CONTENT", "Why F1", 0, "Footprint",
      t("F1 races **where Adyen has offices**, and 457M fans live in Adyen's markets"),
      "Source: F1 2027 calendar and Adyen office list as supplied to SPORTFIVE (calendar not independently confirmed); GWI (F1 audience by market, 2026 vs 2022); map: Adyen.",
      REGIONS.map(([r, o, rc]) => `${r}: offices ${o.join(", ")}; races ${rc.length ? rc.join(", ") : "none"}.`).join("\n") +
      "\n28 offices and 24 races are counted from this list. Adyen's 22 office markets: 457.2M F1 fans in 2026 vs 342.3M in 2022 (+33.6%); 13 of 22 host a 2027 race. China 122.6M; India 117.4M (+94.9%, no race); Japan 7.1M (+41.2%). Full market chart in the backup slides.");
    const cx = [L, L + 1.95, L + 5.0], ry = 2.42, rh = 0.47;
    label(s, "Region", cx[0], 2.0, 1.8);
    label(s, "Adyen offices (28)", cx[1], 2.0, 3.0);
    label(s, "F1 races 2027 (24)", cx[2], 2.0, 2.6);
    REGIONS.forEach(([region, offices, races], i) => {
      const y = ry + i * rh;
      s.addShape(S.LINE, { x: L, y, w: 7.35, h: 0, line: { color: C.accent4, width: 0.75 } });
      s.addText(region, { x: cx[0], y, w: 1.9, h: rh, fontSize: 12.5, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
      const mark = (n, x0, shape, color) => {
        s.addText(String(n), { x: x0, y, w: 0.35, h: rh, fontSize: 12.5, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
        for (let k = 0; k < n; k++)
          s.addShape(shape, { x: x0 + 0.4 + k * 0.19, y: y + rh / 2 - 0.065, w: 0.13, h: 0.13, fill: { color }, line: { color, width: 0 } });
      };
      mark(offices.length, cx[1], S.OVAL, C.accent1);
      mark(races.length, cx[2], S.DIAMOND, C.text1);
    });
    s.addShape(S.LINE, { x: L, y: ry + REGIONS.length * rh, w: 7.35, h: 0, line: { color: C.accent4, width: 0.75 } });
    const ly = ry + REGIONS.length * rh + 0.15;
    s.addShape(S.OVAL, { x: L, y: ly + 0.06, w: 0.13, h: 0.13, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
    s.addText("Adyen office", { x: L + 0.2, y: ly, w: 1.3, h: 0.25, fontSize: 10, color: C.text2, margin: 0, isTextBox: true });
    s.addShape(S.DIAMOND, { x: L + 1.5, y: ly + 0.06, w: 0.13, h: 0.13, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
    s.addText("F1 race weekend", { x: L + 1.7, y: ly, w: 1.6, h: 0.25, fontSize: 10, color: C.text2, margin: 0, isTextBox: true });
    const x = 8.3, w = R - x;
    await fit(s, "adyen_map.jpg", x, 1.9, w, 1.55, "Adyen global acquiring footprint map");
    const tiles = [["457.2M", "F1 fans in Adyen's 22 office markets, +33.6% since 2022", true], ["13 of 22", "Adyen office markets host a 2027 race", false],
      ["India · 117.4M", "+94.9% since 2022; no Grand Prix", false], ["Japan · 7.1M", "+41.2% since 2022", false]];
    const tw = (w - 0.2) / 2, th = 1.3;
    tiles.forEach(([big, lab, dark], i) => {
      const tx = x + (i % 2) * (tw + 0.2), ty = 3.65 + Math.floor(i / 2) * (th + 0.2);
      card(s, tx, ty, tw, th, dark ? C.text1 : C.background2);
      s.addText(big, { x: tx + 0.2, y: ty + 0.15, w: tw - 0.4, h: 0.45, fontSize: 18, bold: true, color: dark ? C.accent1 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: tx + 0.2, y: ty + 0.65, w: tw - 0.4, h: 0.6, fontSize: 10.5, color: dark ? C.accent4 : C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
  }

  // ================================================================ 02 Hospitality
  pres.addSection({ title: "Hospitality" });
  {
    const s = content("CONTENT", "Hospitality", 1, "The B2B platform",
      t("F1 hospitality turns guests into **retention, pipeline and new merchants**"),
      "Source: SPORTFIVE; team partner portfolios (team deck). Photos: team deck.",
      "Team deck slide 13, the ultimate B2B platform: exclusive experiences, a qualified audience and visibility with a high-value enterprise buyer universe, inside partner portfolios of 350+ global brands. 24 race weekends: the 2027 calendar.");
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

  // F1 partner case studies (team deck slides 22-23, incl. George's Businessolver x Alpine material)
  {
    const s = content("CONTENT", "Hospitality", 1, "Proof from F1 partners",
      t("F1 partners report **real commercial returns** from hosting at races"),
      "Source: Komatsu × Williams, HPE × Mercedes and Businessolver × Alpine case material, as compiled by SPORTFIVE (team deck slides 22–23).",
      "Three partners, three proof points: orders closed at races (Komatsu), revenue opportunity accelerated (HPE) and pipeline influenced (Businessolver, an Alpine partner). HPE has partnered the Mercedes F1 team since 2018.");
    const cw = (CW - 0.6) / 3, y = 1.95, h = 4.8, ih = 1.3;
    const cases = [
      { img: null, logo: "case_komatsu_logo.jpg", pair: "Komatsu × Williams", big: "$100M+", lab: "orders received at races",
        body: "Komatsu hosts key global stakeholders at races, many attending a Komatsu event for the first time.",
        stats: [["3,735", "stakeholders hosted"], ["90%", "found it useful for business"], ["94%", "guest satisfaction"]] },
      { img: null, hpe: true, pair: "HPE × Mercedes", big: "$300M+", lab: "revenue opportunity accelerated from race activations alone",
        quote: "\"The real value has been the ability to authentically showcase our technology through Mercedes F1 use cases ... and through direct customer engagement at races.\"",
        by: "Antonio Neri, CEO, HPE · partner since 2018" },
      { img: "case_businessolver.jpg", pair: "Businessolver × Alpine", big: "$122M", lab: "business pipeline, influenced by at-track hosting and experiences",
        body: "Delivering delight. Technology with heart: technology powered by people, with AI, decision-support and real-time analytics.",
        tag: "An Alpine partner: proof from Route 2" },
    ];
    for (const [i, c] of cases.entries()) {
      const x = L + i * (cw + 0.3);
      const dark = i === 1;
      card(s, x, y, cw, h, dark ? C.text1 : C.background2);
      if (c.img) await photo(s, c.img, x, y, cw, ih, c.pair);
      else if (c.hpe) {
        s.addShape(S.RECTANGLE, { x, y, w: cw, h: ih, fill: { color: "0B0F14" }, line: { color: "0B0F14", width: 0 } });
        await fit(s, "case_hpe_neri.jpg", x + cw - 1.15, y, 1.15, ih, "Antonio Neri, CEO, Hewlett Packard Enterprise", "left");
        await fit(s, "case_hpe_logos.jpg", x + 0.2, y + 0.25, cw - 1.55, ih - 0.5, "HPE and Mercedes-AMG Petronas F1 Team logos");
      } else {
        s.addShape(S.RECTANGLE, { x, y, w: cw, h: ih, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
        await fit(s, c.logo, x + 0.6, y + 0.3, cw - 1.2, ih - 0.6, "Komatsu logo");
      }
      s.addText(c.pair.toUpperCase(), { x: x + 0.25, y: y + ih + 0.15, w: cw - 0.5, h: 0.28, fontSize: 10.5, bold: true, charSpacing: 1,
        color: dark ? C.accent1 : C.accent2, margin: 0, isTextBox: true });
      s.addText(c.big, { x: x + 0.25, y: y + ih + 0.45, w: cw - 0.5, h: 0.6, fontSize: 32, bold: true, color: dark ? C.accent1 : C.text1,
        margin: 0, isTextBox: true, valign: "top" });
      s.addText(c.lab, { x: x + 0.25, y: y + ih + 1.08, w: cw - 0.5, h: 0.5, fontSize: 11.5, bold: true, color: dark ? C.background1 : C.text1,
        margin: 0, isTextBox: true, valign: "top" });
      if (c.body) s.addText(c.body, { x: x + 0.25, y: y + ih + 1.62, w: cw - 0.5, h: 0.85, fontSize: 10.5, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
      if (c.stats) {
        const sw = (cw - 0.5) / 3;
        c.stats.forEach(([b, l], k) => s.addText([{ text: b, options: { bold: true, color: C.text1, fontSize: 15, breakLine: true } },
          { text: l, options: { color: C.text2, fontSize: 9 } }],
        { x: x + 0.25 + k * sw, y: y + ih + 2.55, w: sw - 0.08, h: 0.8, margin: 0, isTextBox: true, valign: "top" }));
      }
      if (c.quote) {
        s.addText(c.quote, { x: x + 0.25, y: y + ih + 1.62, w: cw - 0.5, h: 1.2, fontSize: 10.5, italic: true, color: C.accent4, margin: 0, isTextBox: true, valign: "top" });
        s.addText(c.by, { x: x + 0.25, y: y + ih + 2.95, w: cw - 0.5, h: 0.35, fontSize: 10, bold: true, color: C.background1, margin: 0, isTextBox: true });
      }
      if (c.tag) {
        s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.25, y: y + ih + 2.6, w: cw - 0.5, h: 0.45, rectRadius: 0.08, fill: { color: C.accent6 },
          line: { color: C.accent1, width: 1 } });
        s.addText(c.tag, { x: x + 0.4, y: y + ih + 2.6, w: cw - 0.8, h: 0.45, fontSize: 10.5, bold: true, color: C.accent2, margin: 0, isTextBox: true, valign: "middle" });
      }
    }
  }

  // Partner networks (team deck slides 15-17 combined)
  {
    const s = content("CONTENT", "Hospitality", 1, "Partner networks",
      t("Mercedes, McLaren and Ferrari bring the **largest partner networks**"),
      "Source: SPORTFIVE analysis (team deck). 2024–25 public data; estimates where no disclosure. USD at 2024–25 average FX. Audi not in the partner-count analysis.",
      "Combined revenue of each team's partners, the three largest partners by reported revenue, total partners, and FS&I (financial services and insurance) partners. Team note: figures being re-checked (GF). Market-cap tiers and the full sector mapping are in the backup slides.");
    label(s, "Partners' total combined revenue ($ billion)", L, 2.0, 5.6);
    const hi = (n) => n === "Alpine" || n === "Ferrari";
    s.addChart(pres.charts.BAR, [{ name: "Combined revenue ($B)", labels: NETWORK.map((r) => r[0]), values: NETWORK.map((r) => r[1]) }], {
      x: L - 0.1, y: 2.3, w: 5.7, h: 4.45, barDir: "bar", ...chartBase(), catAxisOrientation: "maxMin", barGapWidthPct: 40,
      chartColors: NETWORK.map((r) => (hi(r[0]) ? HEX.green : HEX.context)), dataLabelFormatCode: '"$"#,##0"B"',
      catAxisLabelFontSize: 10.5, dataLabelFontSize: 10.5, valAxisMinVal: 0, valAxisMaxVal: 1300,
    });
    const x = 6.45, w = R - x;
    const cell = (txt, team, o = {}) => ({ text: txt, options: { color: C.text1, fontSize: 10, valign: "middle", fill: { color: hi(team) ? C.accent6 : C.background1 }, ...o } });
    const rows = [[hc("Team", { fontSize: 10 }), hc("Partners", { fontSize: 10, align: "center" }), hc("Top 3 partners by revenue", { fontSize: 10 }), hc("FS&I", { fontSize: 10, align: "center" })],
      ...NETWORK.map(([team, , top]) => [
        cell(team, team, { bold: true }), cell(PARTNERS[team] === null ? "–" : String(PARTNERS[team]), team, { align: "center" }),
        cell(top, team, { color: C.text2 }), cell(String(FSI[team]), team, { align: "center" }),
      ])];
    s.addTable(rows, { x, y: 2.0, w, colW: [1.45, 0.85, 3.23, 0.75], rowH: [0.38, ...NETWORK.map(() => 0.36)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.08, 0.03, 0.08], objectName: "Partner network table" });
  }

  // ================================================================ 03 Adyen in F1
  pres.addSection({ title: "Adyen in F1" });
  // Payments grid
  {
    const s = content("CONTENT", "Adyen in F1", 2, "The category",
      t("Payments is one of F1's **most contested categories**"),
      "Source: SPORTFIVE analysis (BI competitor scan, team deck). Team names as used in the scan.",
      "Four payment brands already partner F1 teams. Two are Adyen competitors (Stripe at Mercedes, Airwallex at McLaren). Two are card schemes (Mastercard in the McLaren Mastercard team name, Visa in the Visa Cash App Racing Bulls team name). Across sport, Adyen's competitors hold 32 properties in the scan: F1 2, football 11, US leagues and college 12, other sport and venues 7 (counted from the team deck's table; full table in the backup slides).");
    const counters = [["4", "payment brands partner F1 teams", C.text1], ["2", "are Adyen competitors: Stripe, Airwallex", C.text1],
      ["2", "are card schemes: Mastercard, Visa", C.accent2]];
    const cw3 = (CW - 0.6) / 3;
    counters.forEach(([big, lab, col], i) => {
      const x = L + i * (cw3 + 0.3);
      s.addText(big, { x, y: 1.9, w: 0.75, h: 0.8, fontSize: 44, bold: true, color: col, margin: 0, isTextBox: true, valign: "middle" });
      s.addText(lab, { x: x + 0.8, y: 1.9, w: cw3 - 0.8, h: 0.8, fontSize: 13, color: C.text1, margin: 0, isTextBox: true, valign: "middle" });
    });
    const grid = [
      ["Stripe", "Mercedes-AMG Petronas", "comp"], ["Airwallex", "McLaren", "comp"],
      ["Mastercard", "McLaren", "scheme"], ["Visa", "Visa Cash App Racing Bulls", "scheme"], ["adyen", "Max Verstappen, Alpine or Ferrari", "adyen"],
    ];
    const tw = (CW - 4 * 0.25) / 5, ty = 2.95, th = 3.0;
    const arrowGrey = await icon("FiArrowDown", "8F97A3"), arrowGreen = await icon("FiArrowDown", "0ABF53");
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
      s.addImage({ data: isA ? arrowGreen : arrowGrey, x: x + tw / 2 - 0.2, y: ty + 1.33, w: 0.4, h: 0.4 });
      s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.2, y: ty + 1.88, w: tw - 0.4, h: 0.9, rectRadius: 0.06,
        fill: { color: isA ? C.background1 : kind === "comp" ? C.text1 : C.accent5 }, line: { color: isA ? C.accent1 : C.text1, width: isA ? 1 : 0 } });
      s.addText([{ text: isA ? "ROUTE IN" : "F1 TEAM", options: { fontSize: 8.5, bold: true, color: isA ? C.accent2 : C.accent1, charSpacing: 1, breakLine: true } },
        { text: team, options: { fontSize: 12, bold: true, color: isA ? C.text1 : C.background1 } }],
      { x: x + 0.3, y: ty + 1.88, w: tw - 0.6, h: 0.9, align: "center", valign: "middle", margin: 0, isTextBox: true });
    }
    card(s, L, 6.1, CW, 0.65, C.accent6, "So what");
    s.addText([{ text: "So what  ", options: { bold: true, color: C.accent2 } },
      { text: "competitors are in, and schemes co-exist with platforms at McLaren: Adyen's seat is open. Across sport, Adyen's competitors hold ", options: { color: C.text1 } },
      { text: "32 properties; only 2 are in F1.", options: { color: C.text1, bold: true } }],
    { x: L + 0.25, y: 6.1, w: CW - 0.5, h: 0.65, fontSize: 12, margin: 0, isTextBox: true, valign: "middle" });
  }

  // Airwallex x McLaren: benchmark and proof (team deck slides 9, 24, 25)
  {
    const s = content("CONTENT", "Adyen in F1", 2, "Airwallex × McLaren",
      t("The model to beat: Airwallex × McLaren, **integration not a logo**"),
      "Source: SPORTFIVE (team deck: competitor scan, credentials); McLaren Racing modernises cross-border payments with Airwallex (Airwallex case study).",
      "Challenge: McLaren Racing operates across 24 race locations with frequent international supplier payments; ~30 manual payments per run, high FX and transfer fees, 2–5 day settlement via banks and SWIFT; the cost cap makes efficiency matter. Solution: implemented in 14 days; batch payouts, approval workflows, faster cross-border transfers; suppliers paid in local currencies; integrated with banking and accounting.");
    await photo(s, "airwallex_carbon.jpg", L, 1.95, 3.3, 4.0, "Airwallex branding on McLaren carbon fibre");
    const mx = 4.2, mw = 3.85;
    const blocks = [
      ["The challenge", "McLaren pays suppliers across 24 race locations: around 30 manual international payments per run, high FX fees and 2–5 day settlement, under F1's cost cap."],
      ["The solution", "Airwallex went live in 14 days: batch payouts, approvals and local-currency payments, integrated with banking and accounting."],
      ["The platform play", "Showcased its payment solutions to enterprises worldwide; a B2B sports portfolio with McLaren, Arsenal FC, San Francisco Giants and Essendon FC."],
    ];
    blocks.forEach(([h, b], i) => {
      const by = 1.95 + i * 1.36;
      label(s, h, mx, by, mw, C.accent2);
      s.addText(b, { x: mx, y: by + 0.3, w: mw, h: 1.0, fontSize: 11.5, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
    });
    const x = 8.35, w = R - x, tw = (w - 0.2) / 2, th = 1.2;
    const tiles = [["14 days", "to go live"], ["90%", "of payments arrive within hours"], ["65%", "of payments arrive instantly"],
      ["110+", "countries on local payment networks"], ["0.5 day", "saved per month on payment runs"], ["£4,000+", "saved a year on transaction and FX fees"]];
    tiles.forEach(([big, lab], i) => {
      const tx = x + (i % 2) * (tw + 0.2), ty = 1.95 + Math.floor(i / 2) * (th + 0.2);
      const dark = i < 2;
      card(s, tx, ty, tw, th, dark ? C.text1 : C.background2);
      s.addText(big, { x: tx + 0.2, y: ty + 0.12, w: tw - 0.4, h: 0.5, fontSize: 21, bold: true, color: dark ? C.accent1 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: tx + 0.2, y: ty + 0.65, w: tw - 0.4, h: 0.5, fontSize: 10.5, color: dark ? C.accent4 : C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    card(s, L, 6.15, CW, 0.6, C.accent6, "Lesson");
    s.addText([{ text: "For Adyen  ", options: { bold: true, color: C.accent2 } },
      { text: "lead with where Adyen sits in the partner's business, show a clear line to revenue, and put hospitality at the centre.", options: { color: C.text1 } }],
    { x: L + 0.25, y: 6.15, w: CW - 0.5, h: 0.6, fontSize: 12.5, margin: 0, isTextBox: true, valign: "middle" });
  }

  // SPORTFIVE credentials (team deck slide 24)
  {
    const s = content("CONTENT", "Adyen in F1", 2, "SPORTFIVE credentials",
      t("This is what we've done: **Airwallex × McLaren**, powering performance"),
      "Source: SPORTFIVE (team deck). Images: McLaren Racing and Airwallex.",
      "SPORTFIVE's flagship F1 payments credential.");
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

  // Business integration
  {
    const s = content("CONTENT", "Adyen in F1", 2, "Business integration",
      t("Where Adyen sits **inside the partner's business**"),
      "Source: Adyen ('Racing | Unified Payments' value chain); Alpine Provisional Rights Overview 2027–2029; Max Verstappen × Adyen proposal; team deck (Alpine partner count).",
      "Integration first, not a logo deal. Top: Adyen's racing value chain, one platform from fan to business bank account. Each step shows what it means on the Alpine and Max routes; Ferrari is still to explore.");
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
    soWhat(s, "**integration first, not a logo deal**: Max, Alpine and Ferrari are each judged on how deeply Adyen sits in the commerce.", 6.2);
  }

  // The return
  {
    const s = content("CONTENT", "Adyen in F1", 2, "The return",
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
      card(s, x, y, cw, h);
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
  pres.addSection({ title: "The routes" });
  // Routes overview
  {
    const s = content("CONTENT", "The routes", 3, "Overview",
      t("Three routes into F1: **Max Verstappen, Alpine and Ferrari**"),
      "Source: Max Verstappen × Adyen proposal (Oct 2026, for discussion); Alpine F1 Team Provisional Rights Overview 2027–2029; SPORTFIVE partner analysis (team deck).",
      "Max and Alpine come from conversations already under way and have proposals on the table. Ferrari has no proposal yet. The aim is buy-in to F1 first; then expand.");
    const cw = (CW - 0.6) / 3;
    const routes = [
      { n: 1, type: "Driver", name: "Max Verstappen", img: "max_banner.jpg", status: "Proposal: for discussion", fields: [
        ["Opportunity", "Official ambassador; Adyen powers the Verstappen business ecosystem"],
        ["Where Adyen sits", "Verstappen Travel tickets and trailers; Pro Simulation booking"],
        ["Terms", "2027–2030, non-exclusive; fee not yet quoted"]] },
      { n: 2, type: "Team", name: "Alpine F1 Team", img: "alpine_engine.jpg", status: "Proposal: provisional", fields: [
        ["Opportunity", "Exclusive Financial Technology Platform Partner, global"],
        ["Where Adyen sits", "Powers the Team's new ecommerce platform, then hospitality and network"],
        ["Terms", "2027–2029; £10.0M in 2027, +5% a year"]] },
      { n: 3, type: "Team", name: "Scuderia Ferrari", img: "f1_city.jpg", status: "To explore", fields: [
        ["Opportunity", "Third-largest partner network in F1: $705B partner revenue"],
        ["Where Adyen sits", "To explore with Ferrari"],
        ["Terms", "No proposal yet"]] },
    ];
    for (const [i, r] of routes.entries()) {
      const x = L + i * (cw + 0.3), y = 1.95;
      card(s, x, y, cw, 3.95);
      await photo(s, r.img, x + 0.2, y + 0.2, cw - 0.4, 0.95, r.name);
      label(s, `Route ${r.n} · ${r.type}`, x + 0.3, y + 1.3, 1.9, C.accent2);
      const pillW = 1.55;
      s.addShape(S.ROUNDED_RECTANGLE, { x: x + cw - 0.3 - pillW, y: y + 1.27, w: pillW, h: 0.28, rectRadius: 0.14,
        fill: { color: r.n === 3 ? C.background1 : C.accent6 }, line: { color: r.n === 3 ? C.accent3 : C.accent6, width: 1 } });
      s.addText(r.status, { x: x + cw - 0.3 - pillW, y: y + 1.27, w: pillW, h: 0.28, fontSize: 8.5, bold: true, color: r.n === 3 ? C.text2 : C.accent2,
        align: "center", valign: "middle", margin: 0, isTextBox: true });
      s.addText(r.name, { x: x + 0.3, y: y + 1.58, w: cw - 0.6, h: 0.42, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
      r.fields.forEach(([f, v], k) => {
        s.addText([{ text: f, options: { bold: true, color: C.text1, breakLine: true } }, { text: v, options: { color: C.text2 } }],
          { x: x + 0.3, y: y + 2.1 + k * 0.6, w: cw - 0.6, h: 0.58, fontSize: 10.5, margin: 0, isTextBox: true, valign: "top" });
      });
    }
    const steps = [["1  Start", "Commit to F1 through Max, Alpine or Ferrari"], ["2  Prove", "Payments live inside the partner's business"],
      ["3  Expand", "More teams, races and markets"]];
    const sw = (CW + 0.15 * 2) / 3;
    steps.forEach(([head, sub], i) => {
      const x = L + i * (sw - 0.15);
      s.addShape(i === 0 ? S.PENTAGON : S.CHEVRON, { x, y: 6.08, w: sw, h: 0.65, fill: { color: i === 0 ? C.accent1 : i === 2 ? C.text1 : C.accent5 },
        line: { color: C.background1, width: 1.5 } });
      s.addText([{ text: head + "   ", options: { bold: true, color: i === 0 ? C.text1 : C.background1, fontSize: 12 } },
        { text: sub, options: { color: i === 0 ? C.text1 : C.accent4, fontSize: 11 } }],
      { x: x + 0.45, y: 6.08, w: sw - 0.8, h: 0.65, margin: 0, isTextBox: true, valign: "middle" });
    });
  }

  // Route 1: Max Verstappen
  {
    const s = content("CONTENT_PHOTO", "The routes", 3, "Route 1 · Max Verstappen",
      t("Max Verstappen: **F1's most popular driver**, and a business ecosystem"),
      "Source: Max Verstappen × Adyen proposal (October 2026); Nielsen Sports as cited. Visual: Max's team, logo placement for illustration.",
      "Four-time World Champion (2021–2024); 71 Grand Prix wins, 48 poles, 131 podiums. Nielsen Sports research names him the most popular driver on the grid. Social: Instagram 19M, X 4.6M, Facebook 3M, YouTube 1M; Verstappen.com channels add Instagram 2M, Threads 800K, TikTok 730K, X 300K. The team deck gives Instagram as 19.3M.");
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
  // Max business ecosystem + what Max's proposal includes
  {
    const s = content("CONTENT", "The routes", 3, "Route 1 · Business opportunity",
      t("Where Adyen fits in Max's business: **Verstappen Travel first**"),
      "Source: SPORTFIVE assessment (team deck slide 29); Max Verstappen × Adyen proposal, October 2026 (for discussion; mock-ups: logo placement for illustration only).",
      "Columns 1–3 are the team deck's assessment as written; blank Adyen-product cells are marked 'To define with Adyen'. Column 4 is what Max's own proposal includes for each business line. The store runs with Fanatics: the full Red Bull Racing and Max Verstappen collections online.");
    const vfill = { yes: C.accent6, no: C.background2, maybe: C.background1 };
    const rows = [[hc("Max's business", { fontSize: 10 }), hc("Adyen products", { fontSize: 10 }), hc("Can Adyen run it?", { fontSize: 10 }), hc("In Max's proposal", { fontSize: 10, fill: { color: C.accent2 } })],
      ...MAX_BUSINESS.map(([biz, prod, what, can, v], i) => {
        const first = can.split(/(?<=[.,])\s/)[0];
        const prop = MAX_PROPOSAL[i], inProp = !prop.startsWith("Not");
        return [
          { text: [{ text: biz, options: { bold: true, color: C.text1, breakLine: true } }, { text: what, options: { color: C.text2, fontSize: 8 } }],
            options: { fontSize: 9, valign: "middle" } },
          prod ? { text: prod, options: { color: C.text1, fontSize: 9, valign: "middle" } }
            : { text: "To define with Adyen", options: { italic: true, color: C.accent3, fontSize: 9, valign: "middle" } },
          { text: [{ text: first + " ", options: { bold: true, color: v === "yes" ? C.accent2 : C.text1 } },
            { text: can.slice(first.length).trim(), options: { color: C.text2 } }], options: { fontSize: 9, valign: "middle", fill: { color: vfill[v] } } },
          { text: prop, options: { fontSize: 9, valign: "middle", color: inProp ? C.text1 : C.accent3, italic: !inProp, bold: false,
            fill: { color: inProp ? C.accent6 : C.background1 } } },
        ];
      })];
    s.addTable(rows, { x: L, y: 1.5, w: 8.85, colW: [3.05, 1.2, 2.3, 2.3], rowH: [0.34, ...MAX_BUSINESS.map(() => 0.56)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.07, 0.03, 0.07], objectName: "Max business table" });
    const x = 9.75, w = R - x, ih = 2.2;
    await photo(s, "max_mock_tickets.jpg", x, 1.5, w, ih, "MV Official Tickets shop, powered by Adyen (mock-up)");
    s.addText("MV Official Tickets shop, powered by Adyen", { x, y: 1.5 + ih + 0.05, w, h: 0.25, fontSize: 9.5, color: C.accent3, margin: 0, isTextBox: true });
    await photo(s, "max_mock_app.jpg", x, 4.15, w, ih, "Orange Army app, powered by Adyen (mock-up)");
    s.addText("Orange Army app, powered by Adyen", { x, y: 4.15 + ih + 0.05, w, h: 0.25, fontSize: 9.5, color: C.accent3, margin: 0, isTextBox: true });
  }
  // Max rights
  {
    const s = content("CONTENT", "The routes", 3, "Route 1 · Rights package",
      t("Rights package: **Max Verstappen × Adyen**"),
      "Source: Max Verstappen × Adyen proposal (October 2026), for discussion purposes. Mock-ups: logo branding for illustration only.",
      "Transcribed from Max's proposal. The GT3 car position reads 'to discuss (not full car)'. Paddock Club hospitality is a SPORTFIVE addition from the team deck: Max's own package excludes Red Bull assets and hospitality, so confirm how it is delivered.");
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

  // Route 2: Alpine
  {
    const s = content("CONTENT", "The routes", 3, "Route 2 · Alpine F1 Team",
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
    const s = content("CONTENT", "The routes", 3, "Route 2 · Business opportunity",
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
    const s = content("CONTENT", "The routes", 3, "Route 2 · Rights overview",
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

  // Route 3: Ferrari (kept small: what we know)
  {
    const s = content("CONTENT", "The routes", 3, "Route 3 · Scuderia Ferrari",
      t("Scuderia Ferrari: **the third-largest partner network** in F1"),
      "Source: SPORTFIVE partner network analysis (team deck); GWI (2026). Figures under review by the team.",
      "No Ferrari proposal yet. Whether to open a conversation is a next step.");
    await photo(s, "f1_city.jpg", L, 1.95, 4.3, 4.7, "F1 car at speed");
    const x = L + 4.65, w = R - x;
    const stats = [["$705B", "combined revenue of Ferrari's partners: #3 of 11 teams"], ["40", "partners, half of them public companies"],
      ["1.80M", "Ferrari fans working in financial services: the largest of any team"], ["5", "FS&I partners already in the network"]];
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
      { text: "No proposal yet: to explore. Whether to open a conversation with Ferrari is one of the next steps.", options: { color: C.background1, fontSize: 13 } }],
    { x: x + 0.3, y: 5.45, w: w - 0.6, h: 1.2, margin: 0, isTextBox: true, valign: "middle" });
  }

  // ================================================================ 05 Next steps
  pres.addSection({ title: "Next steps" });
  {
    const s = content("CONTENT", "Next steps", 4, "Next steps",
      t("Next steps: **from review to launch**"),
      "Source: SPORTFIVE. Review date: team deck.",
      "Six steps, in order. The first is the Chairman's review of the Max and Alpine proposals; Ferrari is a decision in step 4.");
    await photo(s, "paddock_tour.jpg", 8.15, 1.95, R - 8.15, 4.75, "Paddock tour with guests");
    const steps = [["Chairman reviews the Max and Alpine proposals", "Week of 9 November 2026"], ["Gather feedback", null],
      ["Explore or revisit the rights packages", null], ["Open a conversation with Ferrari, or not", null],
      ["Contract and integration plan", null], ["Launch", null]];
    s.addShape(S.LINE, { x: L + 0.27, y: 2.25, w: 0, h: 4.0, line: { color: C.accent4, width: 2 } });
    steps.forEach(([st, when], i) => {
      const y = 1.95 + i * 0.8;
      const first = i === 0, last = i === steps.length - 1;
      s.addShape(S.OVAL, { x: L, y, w: 0.55, h: 0.55, fill: { color: first || last ? C.accent1 : C.text1 }, line: { color: C.background1, width: 2 } });
      s.addText(String(i + 1), { x: L, y, w: 0.55, h: 0.55, fontSize: 15, bold: true, color: first || last ? C.text1 : C.background1, align: "center",
        valign: "middle", margin: 0, isTextBox: true });
      s.addText(when ? [{ text: st, options: { bold: true, color: C.text1, fontSize: 17, breakLine: true } }, { text: when, options: { color: C.accent2, bold: true, fontSize: 12 } }]
        : [{ text: st, options: { bold: true, color: C.text1, fontSize: 17 } }],
      { x: L + 0.8, y: y - 0.02, w: 6.6, h: 0.7, margin: 0, valign: when ? "top" : "middle", isTextBox: true });
    });
  }

  // ================================================================ Appendix
  pres.addSection({ title: "Appendix" });
  {
    const s = content("CONTENT", "Appendix", null, "Appendix", t("Sources and notes"), "Prepared by SPORTFIVE for Adyen. Data as supplied; not independently verified unless stated.",
      "Keep this slide: it answers 'where does that number come from?' in the room. Backup slides (hidden) follow: fans in finance, Adyen markets, partner market-cap tiers, sector mapping, competitors in sport, route assessment, Ferrari detail.");
    const src = [
      ["GWI", "Global F1 audience 2022–2026; F1 audience by Adyen office market; sport affinity indices; team fans working in financial services (2026); Alpine fan audience (GWI Core, Q3 2025–Q2 2026)."],
      ["GlobalData", "F1 sponsorship 2020–2025 (new deals only); brands involved in F1 and their combined revenue (2026)."],
      ["Kantar", "BrandZ 2026 Most Valuable Global Brands; Strong Brands Portfolio 2006–2026; IBM and American Express spotlights; Kantar × Google 2026."],
      ["SPORTFIVE", "Competitor scan (not exhaustive); team partner networks: revenue, partner counts, sector mapping (estimates; being re-checked); F1 partner case studies; Airwallex × McLaren credentials."],
      ["Rights holders", "Alpine Formula One Team, Provisional Rights Overview 2027–2029 (not legally binding). Max Verstappen × Adyen proposal, October 2026 (for discussion)."],
      ["Adyen", "Office locations; RSC Anderlecht case study; partnership brief; 'Racing | Unified Payments' imagery and value chain."],
      ["Calculated", "Counts and sums from the sources above: 24 races, 28 offices, 34.4M fans, 56 tickets, £31.5M over 2027–29, competitor property counts, '% above next-best sport'."],
    ];
    src.forEach(([h, b], i) => {
      const y = 1.95 + i * 0.7;
      if (i) s.addShape(S.LINE, { x: L, y: y - 0.08, w: CW, h: 0, line: { color: C.accent4, width: 0.75 } });
      s.addText(h, { x: L, y, w: 2.2, h: 0.6, fontSize: 12.5, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true });
      s.addText(b, { x: L + 2.4, y, w: CW - 2.4, h: 0.6, fontSize: 11, color: C.text2, margin: 0, valign: "top", isTextBox: true });
    });
  }

  // ================================================================ Backup (hidden)
  pres.addSection({ title: "Backup (hidden)" });
  {
    const s = content("CONTENT", "Backup (hidden)", null, "Backup · Fans in finance",
      t("Every team's fans over-index on **working in financial services**"),
      "Source: Global Web Index (2026). Index vs general population (= 100). North America and Europe (excl. Russia). Average of 11 teams.", "Backup for the audience slide.");
    s.hidden = true;
    label(s, "Index vs general population (= 100) · fans in financial services", L, 2.0, 7.6);
    const colorOf = (n) => (n === "Alpine" || n === "Ferrari" ? HEX.green : n.startsWith("11") ? HEX.navy : HEX.context);
    s.addChart(pres.charts.BAR, [{ name: "Index", labels: FIN_FANS.map(([n, , sz]) => `${n}  (${(sz / 1e6).toFixed(2)}M)`), values: FIN_FANS.map((r) => r[1]) }], {
      x: L - 0.1, y: 2.3, w: 11.0, h: 4.45, barDir: "bar", ...chartBase(), catAxisOrientation: "maxMin", barGapWidthPct: 40,
      chartColors: FIN_FANS.map((r) => colorOf(r[0])), dataLabelFormatCode: "0.0", catAxisLabelFontSize: 10.5, dataLabelFontSize: 10.5,
      valAxisMinVal: 0, valAxisMaxVal: 200,
    });
  }
  {
    const s = content("CONTENT", "Backup (hidden)", null, "Backup · Adyen markets",
      t("F1 audience in Adyen's 11 largest office markets"),
      "Source: GWI (F1 audience by market, 2026 vs 2022); Adyen (office markets). Growth rates as reported.", "Backup for the footprint slide. The other 11 markets add 34.4M.");
    s.hidden = true;
    s.addChart(pres.charts.BAR, [{ name: "F1 audience (M)", labels: MARKETS.map(([m, , g]) => `${m}  (${g})`), values: MARKETS.map((m) => m[1]) }], {
      x: L - 0.1, y: 2.0, w: CW, h: 4.6, barDir: "bar", ...chartBase(), catAxisOrientation: "maxMin", barGapWidthPct: 45,
      chartColors: MARKETS.map((m) => (m[3] ? HEX.green : HEX.context)), dataLabelFormatCode: "0.0", catAxisLabelFontSize: 10.5,
      dataLabelFontSize: 10.5, valAxisMinVal: 0, valAxisMaxVal: 140,
    });
  }
  {
    const s = content("CONTENT", "Backup (hidden)", null, "Backup · Partner profile",
      t("Partner market-cap tiers by team"),
      "Source: SPORTFIVE analysis (team deck). Public data; estimates where no disclosure. USD at 2024–25 average FX (Bloomberg/ECB). Audi not included.",
      "Tier 1 mega-cap $200B+; Tier 2 large-cap $50–200B; Tier 3 mid-cap $5–50B; Tier 4 small-cap below $5B. Haas public/private split as supplied (18/78).");
    s.hidden = true;
    const hiCol = (j) => CAPTEAMS[j] === "Alpine" || CAPTEAMS[j] === "Ferrari";
    const rows = [[hc(""), ...CAPTEAMS.map((tm, j) => hc(tm, { align: "center", fontSize: 10.5, fill: { color: hiCol(j) ? C.accent2 : C.text1 } }))],
      ...CAPROWS.map(([lab, ...vals], i) => [
        { text: lab, options: { bold: true, color: C.text1, fontSize: 11, valign: "middle", fill: { color: C.background2 } } },
        ...vals.map((v, j) => ({ text: v, options: { color: C.text1, bold: i === 0, fontSize: i === 1 ? 10.5 : 12, align: "center", valign: "middle",
          fill: { color: hiCol(j) ? C.accent6 : C.background1 } } })),
      ])];
    s.addTable(rows, { x: L, y: 2.0, w: CW, colW: [2.03, ...CAPTEAMS.map(() => 1.01)], rowH: [0.5, ...CAPROWS.map(() => 0.52)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.06, 0.03, 0.06], objectName: "Market cap table" });
  }
  {
    const s = content("CONTENT", "Backup (hidden)", null, "Backup · Sector mapping",
      t("Relevant team partners by sector"),
      "Source: SPORTFIVE partner mapping (team deck). Relevant team partners only, by sector.", "Team note: figures being re-checked (GF).");
    s.hidden = true;
    s.addChart(pres.charts.BAR, SECTOR.series.map(([name, vals]) => ({ name, labels: SECTOR.teams, values: vals.map((v) => v || null) })), {
      x: L - 0.1, y: 1.95, w: CW + 0.2, h: 4.7, barDir: "col", barGrouping: "stacked", ...chartBase(),
      chartColors: [HEX.green, HEX.navy, HEX.g1, HEX.g2, HEX.g3], showValue: true, dataLabelPosition: "ctr", dataLabelColor: "FFFFFF",
      dataLabelFontSize: 10, dataLabelFontBold: true, showLegend: true, legendPos: "t", legendFontSize: 10.5, legendFontFace: "+mn-lt",
      legendColor: HEX.slate, barGapWidthPct: 45, catAxisLabelFontSize: 10.5,
    });
  }
  {
    const s = content("CONTENT", "Backup (hidden)", null, "Backup · Competitors in sport",
      t("Adyen's competitors across sport"),
      "Source: SPORTFIVE BI competitor scan (team deck; not exhaustive). Property types vary; no equivalence of rights, fees or exclusivity implied.",
      "Counts by column: F1 2, football 11, US leagues & college 12, other sport & venues 7.");
    s.hidden = true;
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
  }
  {
    const s = content("CONTENT", "Backup (hidden)", null, "Recommendation · Assessment",
      [{ text: "Why we recommend " }, { text: "[ADD: route]", options: { color: C.accent1 } }],
      "Source: SPORTFIVE assessment against Adyen's partnership brief; rights-holder proposals.",
      "Hidden for now. Evidence in each cell comes from the proposals. Rate each route ● strong, ◐ partial, ○ weak when the recommendation is made.");
    s.hidden = true;
    const crit = [...BRIEF_CRITERIA, "Payments category available"];
    const ev = {
      max: ["Verstappen Travel ticketing and trailers fit directly; the store is held by Fanatics", "Grandstand ticketing (Spa, Austria 2027) and trackside merchandise",
        "Garage tour, track day, paddock meet-and-greets; Paddock Club to be added", "Max's personal business ecosystem; no team partner network",
        "Top follower markets: USA, Brazil, Netherlands, Mexico, UK, Germany", "Non-exclusive ambassador rights"],
      alp: ["Powers agreed parts of the Team's new ecommerce platform", "Checkout, rewards and race-week venue payments; KPIs proposed",
        "56 Paddock Club tickets a year, Enstone events, near-track dinners", "Introductions to 42 Team partners; One Platform Partner Forum",
        "Global rights", "Exclusive Financial Technology Platform category"],
    };
    const rate = { text: "[ ● ◐ ○ ]  ", options: { bold: true, color: C.accent3 } };
    const cell = (txt) => ({ text: [rate, { text: txt, options: { color: C.text1 } }], options: { fontSize: 10, valign: "middle" } });
    const rows = [[hc("Criterion", { fontSize: 12 }), ...ROUTE_NAMES.map((r) => hc(r, { align: "center", fontSize: 12 }))],
      ...crit.map((c, i) => [
        { text: c, options: { color: C.text1, fontSize: 11.5, bold: true, valign: "middle", fill: { color: C.background2 } } },
        cell(ev.max[i]), cell(ev.alp[i]),
        { text: "No proposal yet", options: { italic: true, color: C.accent3, fontSize: 10, align: "center", valign: "middle" } },
      ])];
    s.addTable(rows, { x: L, y: 1.95, w: CW, colW: [3.13, 3.4, 3.4, 2.2], rowH: [0.42, ...crit.map(() => 0.55)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.1, 0.03, 0.1], objectName: "Assessment table" });
  }
  {
    const s = content("CONTENT", "Backup (hidden)", null, "Ferrari · Business opportunity",
      [{ text: "Ferrari: " }, { text: "[ADD: where Adyen sits in Ferrari's business]", options: { color: C.accent3, italic: true } }],
      "Source: [ADD]", "Hidden until a Ferrari proposal exists. Same columns as Max.");
    s.hidden = true;
    const blank = () => ({ text: "[ADD]", options: { italic: true, color: C.accent3, fontSize: 11, valign: "middle" } });
    const rows = [[hc("Ferrari's business"), hc("Adyen products"), hc("What it does"), hc("Can Adyen run it?")],
      ...[0, 1, 2, 3, 4].map(() => [blank(), blank(), blank(), blank()])];
    s.addTable(rows, { x: L, y: 2.0, w: CW, colW: [3.2, 2.2, 3.15, 3.58], rowH: [0.4, 0.62, 0.62, 0.62, 0.62, 0.62],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.04, 0.1, 0.04, 0.1], objectName: "Ferrari business table" });
  }
  {
    const s = content("CONTENT", "Backup (hidden)", null, "Ferrari · Rights package",
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

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
}

build().catch((e) => { console.error(e); process.exit(1); });
