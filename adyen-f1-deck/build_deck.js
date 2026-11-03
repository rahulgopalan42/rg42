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

const OUT = process.argv[2] || "Adyen x F1 - Chairman deck 6.pptx";
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

// ------------------------------------------------------------------ data (SPORTFIVE team partnership network, Nov 2026)
// "New data" slides in the reviewed deck (Team partnership network 1 and 2). Partners as listed on each team's
// official website (Nov 2026), F1 central partners excluded. Revenue = 2025, US$ bn; parent counted once.
const NETWORK = [ // team, combined partner revenue ($bn), top 3 partners by 2025 revenue
  ["McLaren", 1328, "Alphabet $403bn · Dell $114bn · T-Mobile $88bn"],
  ["Mercedes-AMG", 1058, "Microsoft $305bn · Meta $201bn · PepsiCo $94bn"],
  ["Red Bull Racing", 927, "ExxonMobil $324bn · Ford $187bn · AT&T $126bn"],
  ["VCARB", 768, "ExxonMobil $324bn · Ford $187bn · Siemens $92bn"],
  ["Aston Martin", 744, "Aramco $445bn · Honda $143bn · TikTok $30bn"],
  ["Ferrari", 568, "Shell $267bn · IBM $68bn · HP $56bn"],
  ["Alpine", 390, "Boeing $90bn · Eni $88bn · Renault $68bn"],
  ["Haas", 379, "Toyota $337bn · MGM Resorts $18bn · Pirelli $7.9bn"],
  ["Audi", 330, "BP $189bn · Audi $74bn · adidas $29bn"],
  ["Williams", 138, "Barclays $39bn · Komatsu $27bn · BNY $20bn"],
  ["Cadillac", 109, "América Móvil $50bn · 3M $25bn · Tenneco $18bn"],
];
// market-cap segmentation: number of partners per tier (parent company market cap, 31 Dec 2025)
const CAPTEAMS = ["McLaren", "Mercedes-AMG", "Red Bull Racing", "VCARB", "Aston Martin", "Ferrari", "Alpine", "Haas", "Audi", "Williams", "Cadillac", "All teams"];
const CAP = {
  total: [57, 30, 35, 28, 39, 42, 49, 27, 27, 26, 11, 371],
  pub: ["63 / 37", "70 / 30", "57 / 43", "50 / 50", "51 / 49", "60 / 40", "41 / 59", "26 / 74", "37 / 63", "42 / 58", "45 / 55", "51 / 49"],
  tiers: [
    ["Tier 1 · $200bn+", [10, 5, 6, 4, 3, 6, 1, 1, 1, 3, 0, 40]],
    ["Tier 2 · $50–200bn", [11, 11, 4, 2, 6, 3, 6, 0, 4, 2, 2, 51]],
    ["Tier 3 · $5–50bn", [20, 6, 8, 9, 16, 13, 7, 4, 7, 8, 3, 100]],
    ["Tier 4 · under $5bn", [10, 5, 14, 5, 7, 15, 18, 14, 9, 8, 3, 108]],
    ["No market value*", [6, 3, 3, 8, 7, 5, 17, 8, 6, 5, 3, 71]],
  ],
};

// ------------------------------------------------------------------ data (SPORTFIVE: Adyen – F1 Premium Experiences)
// 2027 F1 calendar as shown in SPORTFIVE's F1 Premium Experiences deck for Adyen.
const CALENDAR = [
  ["12–14 Mar", "Bahrain", "Sakhir"], ["19–21 Mar", "Saudi Arabia", "Jeddah"], ["02–04 Apr", "Australia", "Melbourne"],
  ["16–18 Apr", "China", "Shanghai"], ["09–11 Apr", "Japan", "Suzuka"], ["30 Apr–02 May", "Miami", "Miami"],
  ["21–23 May", "Canada", "Montreal"], ["04–06 Jun", "Monaco", "Monaco"], ["18–20 Jun", "Portugal", "Portimão"],
  ["02–04 Jul", "Great Britain", "Silverstone"], ["09–11 Jul", "Austria", "Spielberg"], ["23–25 Jul", "Belgium", "Spa-Francorchamps"],
  ["30 Jul–01 Aug", "Hungary", "Budapest"], ["03–05 Sep", "Italy", "Monza"], ["10–12 Sep", "Spain", "Madrid"],
  ["24–26 Sep", "Azerbaijan", "Baku"], ["01–03 Oct", "Turkey", "Istanbul"], ["08–10 Oct", "Singapore", "Singapore"],
  ["22–24 Oct", "United States", "Austin"], ["29–31 Oct", "Mexico", "Mexico City"], ["05–07 Nov", "Brazil", "São Paulo"],
  ["18–20 Nov", "Las Vegas", "Las Vegas"], ["03–05 Dec", "Qatar", "Lusail"], ["10–12 Dec", "Abu Dhabi", "Yas Island"],
];
const EXAMPLE_RACES = ["Miami", "Great Britain", "Singapore", "United States"];
const ADYEN_OFFICE_RACES = ["Spain", "Mexico", "China", "Singapore", "Brazil"]; // race in a city with an Adyen office (footprint slide)
// Example packages (race overview slides). [name, scope, highlight, price, Red Bull Racing access]
const PACKAGES = [
  { race: "Miami", when: "USA · 30 Apr–2 May", region: "North America", pk: [
    ["Private Villa", "3 days", "Private, climate-controlled suite; all-inclusive food and drink; guest service team", "$250,000", "20 guests", false],
    ["Casa Tua Trackside Club", "3 days", "Intimate lounge with live music, Casa Tua menus and a premium bar", "$12,000", "per person", false],
    ["Vista Club", "3 days", "Two-storey club with a balcony for up-close pit-lane views", "$7,500", "per person", false],
    ["Red Bull Energy Station", "Sunday", "Q&As with Oracle Red Bull Racing drivers Max Verstappen and Isack Hadjar; trackside at Turns 11–12", "$5,250", "per person", true],
  ] },
  { race: "Silverstone", when: "UK · 2–4 Jul", region: "Europe", pk: [
    ["Private Suite", "Sunday or 3 days", "Inner Track access over Brooklands; suite branding options", "$75,000", "24 guests, Sunday ($90,000 for 3 days)", false],
    ["The Vale", "Sunday or 3 days", "New ultra-premium venue at the pit-lane entry; F1 drivers and Team Principals share stories", "$9,950", "per person, Sunday ($14,500 for 3 days)", false],
    ["Red Bull Pole Position", "Sunday or 3 days", "Closest views of the finish line; appearances from Oracle Red Bull Racing drivers", "$7,250", "per person, Sunday ($9,500 for 3 days)", true],
    ["Octane Terrace", "Sunday", "Elevated grandstand view; street food from Michelin-starred chefs", "$2,995", "per person", false],
  ] },
  { race: "Singapore", when: "Singapore · 8–10 Oct", region: "Asia-Pacific", pk: [
    ["Private Suites", "3 days", "Private viewing gallery with panoramic views; suite customisation possible", "$550,000", "35 guests", false],
    ["Red Bull Paddock", "3 days", "Walk-through of the Oracle Red Bull Racing garage; guided pit-lane walks", "$20,500", "per person", true],
    ["Velocity Terrace", "2 or 3 days", "Exclusive track viewing deck; limited capacity, built for networking", "$7,250", "per person", false],
    ["Skyview Pavilion", "3 days", "Air-conditioned lounge with an attached outdoor grandstand", "$4,950", "per person", false],
  ] },
];
const AUSTIN = [ // sample four-day programme, Austin 2027 (date TBC)
  ["Day 1", "Texan welcome", "austin_estate.jpg", "Commodore Perry Estate", [
    "Arrive in Austin; transfer and check in at the Commodore Perry Estate", "Spa treatments to recover from travel", "Dinner at Michelin-starred Hestia"]],
  ["Day 2", "The Austin edit", "austin_skyline.jpg", "Austin skyline", [
    "Hat shaping at Maufrais and boot fitting at Allen Boots", "Private lunch, dinner and wine tasting", "Horseback riding with former F1 World Champion Jenson Button"]],
  ["Day 3", "Full throttle", "austin_cota.jpg", "Guests at Circuit of the Americas", [
    "Race day at Circuit of the Americas from a private suite", "Curated local menus, free-flowing drinks, podium celebration access", "Caviar, champagne and cigars at Room 725"]],
  ["Day 4", "Until the next chequered flag", "hosp_chef.jpg", "Hospitality service", [
    "Breakfast and check-out", "Leave with a weekend of memories and deeper connections"]],
];
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
const ROUTE_NAMES = ["Max Verstappen", "Alpine F1 Team", "Scuderia Ferrari"];

// ------------------------------------------------------------------ slides
// Deck 6: 31 visible slides, no dividers; the tracker at the top right shows the section.
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

  // Why F1 at a glance (replaces the hypothesis slide; the six tiles that sat on the executive summary)
  {
    const s = content("CONTENT", "Introduction", null, "Why F1, at a glance",
      t("F1 gives Adyen **audience, reach, brands, hospitality and a network** on one platform"),
      "Source: GWI (audience 2026; affinity across five sports); GlobalData (2026); Adyen office list; F1 2027 calendar (SPORTFIVE); SPORTFIVE team partnership network (Nov 2026).",
      "Six facts, one per part of the deck. Audience: F1 ranks #1 of the five sports assessed on all five audiences (GWI). Growth: 625.3M followers in 2026, +30.8% vs 2022 (GWI). Brands: 50% of the world's most valuable brands are involved in F1 (GlobalData). Footprint: 457.2M fans in Adyen's 22 office markets; 13 host a 2027 race. Hospitality: 24 race weekends on the 2027 calendar. Network: 371 partners on the 11 teams' rosters with $6.7tn combined 2025 revenue (a partner on two teams is counted for each).");
    const tiles = [
      ["FiUsers", "01", "Audience", "#1", "sport on all five audiences Adyen sells to, of the five sports assessed"],
      ["FiTrendingUp", "02", "Growth", "625M", "F1 followers in 2026, up 30.8% since 2022"],
      ["FiAward", "03", "Brands", "50%", "of the world's most valuable brands are involved in F1"],
      ["FiGlobe", "04", "Footprint", "457M", "F1 fans in Adyen's 22 office markets; 13 of them host a 2027 race"],
      ["FiCoffee", "05", "Hospitality", "24", "race weekends in 2027 to host clients, merchants and prospects"],
      ["FiShare2", "06", "Network", "371", "partners on the 11 teams' rosters, with $6.7tn combined revenue"],
    ];
    const tw = (CW - 0.5) / 3, th = 2.25;
    for (const [i, [ic, n, head, big, body]] of tiles.entries()) {
      const x = L + (i % 3) * (tw + 0.25), y = 1.95 + Math.floor(i / 3) * (th + 0.25);
      const dark = i === 4;
      card(s, x, y, tw, th, dark ? C.text1 : C.background2, "Fact tile");
      await iconDot(s, ic, x + 0.28, y + 0.28, 0.5, C.accent1, dark ? C.text1 : "FFFFFF");
      s.addText([{ text: n + "  ", options: { color: C.accent1, bold: true } }, { text: head.toUpperCase(), options: { color: dark ? C.accent4 : C.text2, bold: true } }],
        { x: x + 0.95, y: y + 0.28, w: tw - 1.2, h: 0.5, fontSize: 11, charSpacing: 1, margin: 0, isTextBox: true, valign: "middle" });
      s.addText(big, { x: x + 0.28, y: y + 0.92, w: tw - 0.56, h: 0.7, fontSize: 38, bold: true, color: dark ? C.accent1 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(body, { x: x + 0.28, y: y + 1.62, w: tw - 0.56, h: 0.55, fontSize: 12, color: dark ? C.accent4 : C.text2, margin: 0, isTextBox: true, valign: "top" });
    }
  }

  // Executive summary: the three routes (the focus the reviewer asked for)
  {
    const s = content("CONTENT", "Introduction", null, "Executive summary",
      t("Three routes into F1: **two proposals on the table**, one to explore"),
      "Source: Max Verstappen × Adyen proposal (Oct 2026, for discussion); Alpine F1 Team Provisional Rights Overview 2027–2029; SPORTFIVE F1 Premium Experiences (hospitality); SPORTFIVE team partnership network (Nov 2026); GWI.",
      "The ask today is buy-in to F1. Max and Alpine come from conversations already under way; Ferrari is the option in reserve. Hospitality can be bundled with the Max route only (SPORTFIVE).");
    const cw = (CW - 0.6) / 3, y = 1.9, h = 4.3, ih = 1.45;
    const routes = [
      { n: 1, type: "Driver", name: "Max Verstappen", img: "max_banner.jpg", status: "Proposal: for discussion", line: "Reach, influence and a business to power",
        pts: ["Official ambassador, 2027–2030", "Adyen powers Verstappen Travel tickets and trackside trailers",
          "Hospitality bundle at the Grands Prix Adyen chooses"] },
      { n: 2, type: "Team", name: "Alpine F1 Team", img: "alpine_engine.jpg", status: "Proposal: for discussion", line: "The full team platform, built on commerce",
        pts: ["Exclusive Financial Technology Platform Partner", "Adyen powers the Team's new ecommerce platform",
          "56 Paddock Club tickets a year; 49 team partners"] },
      { n: 3, type: "Team", name: "Scuderia Ferrari", img: "f1_city.jpg", status: "To explore", line: "The option to keep in reserve",
        pts: ["42 partners, $568bn combined revenue", "1.80M fans in financial services, the most of any team", "No proposal yet"] },
    ];
    const check = await icon("FiCheck", "0ABF53"), dot = await icon("FiCircle", "8F97A3");
    for (const [i, r] of routes.entries()) {
      const x = L + i * (cw + 0.3);
      const hero = r.n !== 3;
      card(s, x, y, cw, h, hero ? C.text1 : C.background2, "Route card");
      await photo(s, r.img, x, y, cw, ih, r.name);
      s.addText(`ROUTE ${r.n} · ${r.type.toUpperCase()}`, { x: x + 0.28, y: y + ih + 0.2, w: 1.9, h: 0.28, fontSize: 10, bold: true, charSpacing: 1,
        color: C.accent1, margin: 0, isTextBox: true, valign: "middle" });
      const pillW = 1.6;
      s.addShape(S.ROUNDED_RECTANGLE, { x: x + cw - 0.28 - pillW, y: y + ih + 0.19, w: pillW, h: 0.3, rectRadius: 0.15,
        fill: { color: hero ? C.accent1 : C.background1 }, line: { color: hero ? C.accent1 : C.accent3, width: 1 } });
      s.addText(r.status, { x: x + cw - 0.28 - pillW, y: y + ih + 0.19, w: pillW, h: 0.3, fontSize: 8.5, bold: true, color: hero ? C.text1 : C.text2,
        align: "center", valign: "middle", margin: 0, isTextBox: true });
      s.addText([{ text: r.name, options: { bold: true, fontSize: 20, color: hero ? C.background1 : C.text1, breakLine: true } },
        { text: r.line, options: { fontSize: 11.5, color: hero ? C.accent4 : C.text2 } }],
      { x: x + 0.28, y: y + ih + 0.58, w: cw - 0.56, h: 0.8, margin: 0, isTextBox: true, valign: "top" });
      r.pts.forEach((pt, k) => {
        const py = y + ih + 1.48 + k * 0.45;
        s.addImage({ data: hero ? check : dot, x: x + 0.28, y: py + 0.06, w: 0.2, h: 0.2 });
        s.addText(pt, { x: x + 0.6, y: py, w: cw - 0.88, h: 0.42, fontSize: 10.5, color: hero ? C.background1 : C.text2, margin: 0, isTextBox: true, valign: "top" });
      });
    }
    card(s, L, 6.35, CW, 0.5, C.accent6, "Ask strip");
    s.addText([{ text: "The ask  ", options: { bold: true, color: C.accent2 } },
      { text: "agree F1 is the right platform for Adyen; start with one route, prove it, then expand.", options: { color: C.text1 } },
      { text: "   Next: Chairman review, w/c 9 November", options: { color: C.accent2, bold: true } }],
    { x: L + 0.25, y: 6.35, w: CW - 0.5, h: 0.5, fontSize: 11.5, margin: 0, isTextBox: true, valign: "middle" });
  }

  // ================================================================ 01 Why F1
  pres.addSection({ title: "Why F1" });
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

  // Growth
  {
    const s = content("CONTENT", "Why F1", 0, "Growth",
      t("F1 is growing in **audience and in commercial value**"),
      "Source: GWI (global audience, followers); GlobalData (new sponsorship deals only, excl. renewals). 2026 YTD: $1.91B across 139 deals, year incomplete.",
      "Audience: 478.0M (2022) to 625.3M (2026), +30.8%, +147.3M followers; +8.3% vs 2025.\nSponsorship: total value of NEW deals, not annual sponsorship revenue. $0.89B (2020) to $2.37B (2025), +165.3%. 125 new deals in 2025 (+28.9%).");
    const cards = [
      { x: L, head: "Global F1 audience", big: "+30.8%", sub: "2022–2026 · 147.3M additional followers", d: AUDIENCE,
        fmt: '0.0"M"', note: "625.3M followers in 2026, +8.3% vs 2025" },
      { x: L + CW / 2 + 0.15, head: "New F1 sponsorship deal value", big: "+165.3%", sub: "2020–2025 · new deals only, excludes renewals", d: DEALS,
        fmt: '"$"0.00"B"', note: "125 new deals in 2025 (+28.9%)" },
    ];
    const cw = CW / 2 - 0.15;
    for (const c of cards) {
      card(s, c.x, 2.0, cw, 4.75);
      label(s, c.head, c.x + 0.3, 2.2, cw - 0.6);
      s.addText(c.big, { x: c.x + 0.3, y: 2.5, w: 2.4, h: 0.6, fontSize: 32, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(c.sub, { x: c.x + 2.55, y: 2.6, w: cw - 2.85, h: 0.45, fontSize: 11, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
      const n = c.d.values.length;
      s.addChart(pres.charts.BAR, [{ name: c.head, labels: c.d.years, values: c.d.values }], {
        x: c.x + 0.15, y: 3.15, w: cw - 0.3, h: 3.05, barDir: "col", ...chartBase(),
        chartColors: c.d.values.map((_, i) => (i === n - 1 ? HEX.green : HEX.context)),
        dataLabelFormatCode: c.fmt, valAxisMinVal: 0,
      });
      s.addText(c.note, { x: c.x + 0.3, y: 6.25, w: cw - 0.6, h: 0.3, fontSize: 11, color: C.text2, margin: 0, isTextBox: true });
    }
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
      "Source: SPORTFIVE; SPORTFIVE team partnership network (Nov 2026); F1 2027 calendar. Photos: team deck.",
      "Team deck slide 13, the ultimate B2B platform: exclusive experiences, a qualified audience and visibility with a high-value enterprise buyer universe. 371 partners: SPORTFIVE team partnership network (Nov 2026), the sum of the 11 teams' rosters. 24 race weekends: the 2027 calendar.");
    const cols = [
      ["hosp_hotlap.jpg", "FiHeart", "Client retention", "Exclusive experiences", "Bonds with clients that traditional hosting cannot match."],
      ["hosp_suite.jpg", "FiTrendingUp", "Pipeline generation", "A qualified audience", "C-suite decision-makers, in market, at every race."],
      ["hosp_terrace.jpg", "FiUserPlus", "Merchant acquisition", "A network of brands", "371 partners on the 11 teams' rosters to meet."],
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
    const strip = [["371", "partners on the 11 teams' rosters"], ["24", "race weekends in 2027 to host clients"], ["8–10", "races in Adyen's first global programme"]];
    const sw = CW / 3;
    strip.forEach(([big, lab], i) => s.addText([{ text: big + "  ", options: { bold: true, color: C.accent1, fontSize: 20 } },
      { text: lab, options: { color: C.background1, fontSize: 11.5 } }],
    { x: L + 0.3 + i * sw, y: 5.95, w: sw - 0.4, h: 0.75, margin: 0, isTextBox: true, valign: "middle" }));
  }

  // Proof from F1 hospitality: Businessolver (George's Alpine material; the reviewer suggested using it) plus two
  // SPORTFIVE references already shown to Adyen in the F1 Premium Experiences deck. Komatsu and HPE removed: confidential.
  {
    const s = content("CONTENT", "Hospitality", 1, "Proof from F1 hospitality",
      t("Hosting at F1 races **turns guests into pipeline**"),
      "Source: Businessolver × Alpine case material (SPORTFIVE); SPORTFIVE references in 'Adyen – F1 Premium Experiences': CommScope × MoneyGram Haas F1 Team, Century Financial (Abu Dhabi GP, Dec 2025).",
      "Komatsu × Williams and HPE × Mercedes have been removed: their source decks are marked highly confidential. CommScope and Century Financial are references from SPORTFIVE's own F1 Premium Experiences deck prepared for Adyen. Businessolver is an Alpine partner (Route 2). Century Financial quote shortened with an ellipsis; full quote: 'Abu Dhabi was more than a race weekend, it was an opportunity to thank our clients and partners by sharing an experience that mirrors our values. Hosting them trackside at the season finale allowed us to connect on a deeper level, in an atmosphere of excitement and significance, and reinforce the relationships that are central to our continued growth.'");
    const cw = (CW - 0.6) / 3, y = 1.95, h = 4.8, ih = 1.45;
    const cases = [
      { img: "case_businessolver.jpg", pair: "Businessolver × Alpine", big: "$122M", lab: "business pipeline, influenced by at-track hosting and experiences",
        body: "Technology with heart: AI, decision-support and real-time analytics, shown to clients through Alpine.", tag: "An Alpine partner: proof from Route 2" },
      { img: "case_commscope.jpg", pair: "CommScope × Haas F1 Team", big: "11 races", lab: "global B2B customer programme, delivered by SPORTFIVE",
        pts: ["Commercial ROI achieved: programme investment recovered through future deal opportunities",
          "ROI tracking linked guest engagement to pipeline and revenue"] },
      { img: "case_abudhabi.jpg", pair: "Century Financial · Abu Dhabi", big: "240 guests", lab: "3 race days, a private space and 4 brand activations, delivered by SPORTFIVE",
        quote: "\u201cHosting them trackside at the season finale allowed us to connect on a deeper level ... and reinforce the relationships that are central to our continued growth.\u201d",
        by: "Chief Institutional Business Officer, Century Financial" },
    ];
    const check = await icon("FiCheck", "0ABF53");
    for (const [i, c] of cases.entries()) {
      const x = L + i * (cw + 0.3);
      const dark = i === 1;
      card(s, x, y, cw, h, dark ? C.text1 : C.background2);
      await photo(s, c.img, x, y, cw, ih, c.pair);
      s.addText(c.pair.toUpperCase(), { x: x + 0.25, y: y + ih + 0.15, w: cw - 0.5, h: 0.28, fontSize: 10.5, bold: true, charSpacing: 1,
        color: dark ? C.accent1 : C.accent2, margin: 0, isTextBox: true });
      s.addText(c.big, { x: x + 0.25, y: y + ih + 0.45, w: cw - 0.5, h: 0.6, fontSize: 32, bold: true, color: dark ? C.accent1 : C.text1,
        margin: 0, isTextBox: true, valign: "top" });
      s.addText(c.lab, { x: x + 0.25, y: y + ih + 1.08, w: cw - 0.5, h: 0.5, fontSize: 11.5, bold: true, color: dark ? C.background1 : C.text1,
        margin: 0, isTextBox: true, valign: "top" });
      if (c.body) s.addText(c.body, { x: x + 0.25, y: y + ih + 1.68, w: cw - 0.5, h: 0.75, fontSize: 10.5, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
      if (c.pts) c.pts.forEach((pt, k) => {
        const py = y + ih + 1.7 + k * 0.62;
        s.addImage({ data: check, x: x + 0.25, y: py + 0.03, w: 0.2, h: 0.2 });
        s.addText(pt, { x: x + 0.55, y: py, w: cw - 0.8, h: 0.6, fontSize: 10.5, color: C.accent4, margin: 0, isTextBox: true, valign: "top" });
      });
      if (c.quote) {
        s.addText(c.quote, { x: x + 0.25, y: y + ih + 1.68, w: cw - 0.5, h: 1.05, fontSize: 10.5, italic: true, color: C.text1, margin: 0, isTextBox: true, valign: "top" });
        s.addText(c.by, { x: x + 0.25, y: y + ih + 2.8, w: cw - 0.5, h: 0.4, fontSize: 9.5, bold: true, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
      }
      if (c.tag) {
        s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.25, y: y + ih + 2.65, w: cw - 0.5, h: 0.45, rectRadius: 0.08, fill: { color: C.accent6 },
          line: { color: C.accent1, width: 1 } });
        s.addText(c.tag, { x: x + 0.4, y: y + ih + 2.65, w: cw - 0.8, h: 0.45, fontSize: 10.5, bold: true, color: C.accent2, margin: 0, isTextBox: true, valign: "middle" });
      }
    }
  }

  // Team partnership network (1): new data, Nov 2026
  {
    const s = content("CONTENT", "Hospitality", 1, "Team partnership network",
      t("**$6.7tn** combined partner revenue across 11 teams; McLaren and Mercedes lead"),
      "Source: SPORTFIVE. Partners as listed on each team's official website (Nov 2026); F1 central partners excluded. 2025 revenue, US$; parent counted once; private companies estimated; company reports, companiesmarketcap.com.",
      "New data (replaces the earlier partner-revenue slide). Oil and car giants lift Red Bull Racing, VCARB and Haas. Where several partners of one team share a parent (e.g. Android, Chrome, Gemini and Google Cloud = Alphabet), the parent is counted once; sub-brands without separate reporting (e.g. Ford Racing, Mobil 1, Toyota Gazoo Racing) are counted at parent revenue. Non-USD figures converted at 2024–25 average FX (Bloomberg/ECB). Top 3 shown by parent: McLaren Alphabet (Android, Chrome, Gemini, Google Cloud); Mercedes Meta (Meta AI, WhatsApp); Red Bull ExxonMobil (Esso, Mobil 1), Ford (Ford Racing); VCARB ExxonMobil (Mobil 1), Ford (Ford Racing); Aston Martin Aramco (incl. Valvoline); Alpine Renault (R5 Turbo, Mobilize); Haas Toyota (Gazoo Racing); Audi BP (bp, Castrol); Cadillac América Móvil (Claro). Gucci is Alpine's Title Partner from 2027.");
    label(s, "Partners' combined revenue, $bn, 2025", L, 1.95, 5.2);
    const hi = (n) => n === "Alpine" || n === "Ferrari";
    s.addChart(pres.charts.BAR, [{ name: "Combined revenue ($bn)", labels: NETWORK.map((r) => r[0]), values: NETWORK.map((r) => r[1]) }], {
      x: L - 0.1, y: 2.25, w: 5.25, h: 4.35, barDir: "bar", ...chartBase(), catAxisOrientation: "maxMin", barGapWidthPct: 40,
      chartColors: NETWORK.map((r) => (hi(r[0]) ? HEX.green : HEX.context)), dataLabelFormatCode: '"$"#,##0"bn"',
      catAxisLabelFontSize: 10.5, dataLabelFontSize: 10.5, valAxisMinVal: 0, valAxisMaxVal: 1600,
    });
    s.addText("* Alpine: Gucci is Title Partner from 2027", { x: L, y: 6.6, w: 5.2, h: 0.25, fontSize: 9.5, italic: true, color: C.text2, margin: 0, isTextBox: true });
    const x = 6.0, w = R - x;
    const cell = (txt, team, o = {}) => ({ text: txt, options: { color: C.text1, fontSize: 10, valign: "middle", fill: { color: hi(team) ? C.accent6 : C.background1 }, ...o } });
    const rows = [[hc("Team", { fontSize: 10 }), hc("Top 3 partners by 2025 revenue", { fontSize: 10 })],
      ...NETWORK.map(([team, , top]) => [cell(team + (team === "Alpine" ? "*" : ""), team, { bold: true }), cell(top, team, { color: C.text2 })])];
    s.addTable(rows, { x, y: 1.95, w, colW: [1.55, w - 1.55], rowH: [0.36, ...NETWORK.map(() => 0.355)],
      border: { type: "solid", pt: 0.75, color: C.accent4 }, margin: [0.03, 0.1, 0.03, 0.1], objectName: "Top partners table" });
  }

  // Team partnership network (2): market-cap segmentation, new data
  {
    const s = content("CONTENT", "Hospitality", 1, "Team partnership network",
      t("Mercedes has the most **blue-chip roster**: 16 of 30 partners worth $50bn+"),
      "Source: SPORTFIVE. Partners as listed on each team's official website (Nov 2026). Parent-company market cap at 31 Dec 2025; private companies at latest known valuation (estimate). Non-USD at 2025 average FX. companiesmarketcap.com; company reports.",
      "New data (replaces the earlier market-cap backup). *No market value: state-owned groups (e.g. PETRONAS, Qatar Airways, Etihad), partnerships (e.g. Deloitte), non-profits, governments and small private firms without a known valuation. Alpine's Tier 3 count includes Gucci. Shading: share of the team's partners in that tier (light 10–25%, medium 25–40%, dark 40%+). The team's own headline adds: Haas and Alpine rely on small, private brands.");
    const hiCol = (j) => CAPTEAMS[j] === "Alpine" || CAPTEAMS[j] === "Ferrari";
    const allCol = (j) => j === CAPTEAMS.length - 1;
    const shade = (v, j) => {
      const share = v / CAP.total[j];
      return share >= 0.4 ? "9FE3BB" : share >= 0.25 ? "C6EFD5" : share >= 0.1 ? "E6F8ED" : "FFFFFF";
    };
    const headFill = (j) => (hiCol(j) ? C.accent2 : C.text1);
    const short = { "Mercedes-AMG": "Mercedes", "Red Bull Racing": "Red Bull", "Aston Martin": "Aston Martin", "All teams": "All teams" };
    const rows = [
      [hc("", { fontSize: 9.5 }), ...CAPTEAMS.map((tm, j) => hc(short[tm] || tm, { align: "center", fontSize: 9.5, fill: { color: headFill(j) } }))],
      [{ text: "Partners", options: { bold: true, color: C.text1, fontSize: 10.5, valign: "middle", fill: { color: C.background2 } } },
        ...CAP.total.map((v, j) => ({ text: String(v), options: { bold: true, color: C.text1, fontSize: 13, align: "center", valign: "middle",
          fill: { color: allCol(j) ? C.background2 : C.background1 } } }))],
      [{ text: "% public / private", options: { bold: true, color: C.text1, fontSize: 10.5, valign: "middle", fill: { color: C.background2 } } },
        ...CAP.pub.map((v, j) => ({ text: v, options: { color: C.text2, fontSize: 9.5, align: "center", valign: "middle",
          fill: { color: allCol(j) ? C.background2 : C.background1 } } }))],
      ...CAP.tiers.map(([lab, vals], i) => [
        { text: lab, options: { bold: true, color: C.text1, fontSize: 10.5, valign: "middle", fill: { color: C.background2 } } },
        ...vals.map((v, j) => ({ text: v ? String(v) + (CAPTEAMS[j] === "Alpine" && i === 2 ? "*" : "") : "–",
          options: { color: i === 4 ? C.text2 : C.text1, fontSize: 12, align: "center", valign: "middle", bold: allCol(j),
            fill: { color: allCol(j) || i === 4 ? C.background2 : shade(v, j) } } })),
      ]),
    ];
    s.addTable(rows, { x: L, y: 1.95, w: CW, colW: [1.85, ...CAPTEAMS.map(() => (CW - 1.85) / CAPTEAMS.length)],
      rowH: [0.5, 0.5, 0.45, 0.5, 0.5, 0.5, 0.5, 0.5], border: { type: "solid", pt: 0.75, color: C.accent4 },
      margin: [0.03, 0.04, 0.03, 0.04], objectName: "Market cap table" });
    const ly = 1.95 + 3.95 + 0.12;
    [["E6F8ED", "10–25%"], ["C6EFD5", "25–40%"], ["9FE3BB", "40%+"]].forEach(([c, lab], i) => {
      s.addShape(S.RECTANGLE, { x: L + i * 1.2, y: ly + 0.05, w: 0.22, h: 0.16, fill: { color: c }, line: { color: C.accent4, width: 0.5 } });
      s.addText(lab, { x: L + 0.28 + i * 1.2, y: ly, w: 0.9, h: 0.26, fontSize: 9.5, color: C.text2, margin: 0, isTextBox: true, valign: "middle" });
    });
    s.addText("Shading: share of the team's partners in that tier.  *No market value: state-owned groups, partnerships, non-profits, governments, small private firms.  Alpine Tier 3 includes Gucci.",
      { x: L + 3.7, y: ly, w: CW - 3.7, h: 0.26, fontSize: 9, color: C.text2, margin: 0, isTextBox: true, valign: "middle" });
    card(s, L, 6.4, CW, 0.48, C.accent6, "Takeaway");
    s.addText([{ text: "For the routes  ", options: { bold: true, color: C.accent2 } },
      { text: "Alpine has the second-largest roster (49 partners), mostly smaller and private brands; Ferrari's 42 include 6 worth $200bn+.", options: { color: C.text1 } }],
    { x: L + 0.25, y: 6.4, w: CW - 0.5, h: 0.48, fontSize: 11.5, margin: 0, isTextBox: true, valign: "middle" });
  }

  // ================================================================ 03 Adyen in F1
  pres.addSection({ title: "Adyen in F1" });
  // The category: one message. Two Adyen competitors already use F1; Adyen is not there yet.
  {
    const s = content("CONTENT", "Adyen in F1", 2, "The category",
      t("Two of Adyen's competitors **already use F1**; Adyen is not there yet"),
      "Source: SPORTFIVE BI competitor scan (team deck; not exhaustive). Team names as used in the scan.",
      "Key message: Adyen's direct competitors are already using F1 team partnerships to put their payments platforms in front of enterprise buyers. Stripe partners Mercedes-AMG Petronas; Airwallex partners McLaren (next slide shows how). Card schemes are also in F1 (Mastercard in the McLaren Mastercard team name; Visa in the Visa Cash App Racing Bulls team name), but they sit in the payment chain with Adyen rather than competing with it. Across sport, Adyen's competitors hold 32 properties in the scan; 2 are in F1 (full table in the backup slides).");
    const cw = (CW - 0.6) / 3, y = 1.95, h = 3.05;
    const cols = [
      { tag: "COMPETITOR · IN F1", brand: "Stripe", team: "Mercedes-AMG Petronas F1 Team", body: "A direct Adyen competitor with an F1 team partnership" },
      { tag: "COMPETITOR · IN F1", brand: "Airwallex", team: "McLaren F1 Team", body: "Runs McLaren's supplier payments and uses the partnership to win enterprise clients (next slide)" },
      { tag: "NOT YET IN F1", brand: "adyen", team: "Route in: Max Verstappen, Alpine or Ferrari", body: "Two proposals on the table: Max and Alpine" },
    ];
    const arrowGrey = await icon("FiArrowDown", "8F97A3"), arrowGreen = await icon("FiArrowDown", "0ABF53");
    for (const [i, c] of cols.entries()) {
      const x = L + i * (cw + 0.3), isA = i === 2;
      if (isA) s.addShape(S.ROUNDED_RECTANGLE, { x, y, w: cw, h, rectRadius: 0.08, fill: { color: C.accent6 },
        line: { color: C.accent1, width: 1.5, dashType: "dash" }, objectName: "Adyen seat" });
      else card(s, x, y, cw, h, C.text1);
      s.addShape(S.ROUNDED_RECTANGLE, { x: x + 0.3, y: y + 0.25, w: 2.0, h: 0.3, rectRadius: 0.15, fill: { color: isA ? C.accent1 : C.accent5 },
        line: { color: isA ? C.accent1 : C.accent5, width: 0 } });
      s.addText(c.tag, { x: x + 0.3, y: y + 0.25, w: 2.0, h: 0.3, fontSize: 8.5, bold: true, color: isA ? C.text1 : C.accent1, align: "center",
        valign: "middle", charSpacing: 1, margin: 0, isTextBox: true });
      if (isA) s.addImage({ path: A("adyen_green.png"), x: x + 0.3, y: y + 0.8, w: 1.7, h: 0.55, altText: "Adyen logo" });
      else s.addText(c.brand, { x: x + 0.3, y: y + 0.75, w: cw - 0.6, h: 0.65, fontSize: 30, bold: true, color: C.background1, margin: 0, isTextBox: true, valign: "middle" });
      s.addImage({ data: isA ? arrowGreen : arrowGrey, x: x + 0.3, y: y + 1.5, w: 0.32, h: 0.32 });
      s.addText(c.team, { x: x + 0.75, y: y + 1.45, w: cw - 1.05, h: 0.45, fontSize: 13.5, bold: true, color: isA ? C.text1 : C.background1, margin: 0,
        isTextBox: true, valign: "middle" });
      s.addShape(S.LINE, { x: x + 0.3, y: y + 2.1, w: cw - 0.6, h: 0, line: { color: isA ? C.accent1 : C.accent5, width: 0.75 } });
      s.addText(c.body, { x: x + 0.3, y: y + 2.2, w: cw - 0.6, h: 0.75, fontSize: 11.5, color: isA ? C.text1 : C.accent4, margin: 0, isTextBox: true, valign: "top" });
    }
    card(s, L, 5.2, CW, 0.95, C.background2, "Why it matters");
    s.addText([{ text: "Why it matters  ", options: { bold: true, color: C.accent2 } },
      { text: "Adyen's rivals are using F1 to put their payments platforms in front of the same enterprise buyers Adyen wants. ", options: { color: C.text1, bold: true } },
      { text: "Across sport they hold 32 properties in our scan; 2 of them are in F1.", options: { color: C.text2 } }],
    { x: L + 0.25, y: 5.2, w: CW - 0.5, h: 0.95, fontSize: 13, margin: 0, isTextBox: true, valign: "middle" });
    s.addText("Card schemes are in F1 too (Mastercard at McLaren, Visa at Visa Cash App Racing Bulls). They work alongside Adyen in the payment chain, so they are not counted as competitors.",
      { x: L, y: 6.3, w: CW, h: 0.45, fontSize: 10, italic: true, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
  }

  // Airwallex x McLaren: how a payments peer uses F1, in three steps (team deck slides 9, 24, 25; Airwallex case study)
  {
    const s = content("CONTENT", "Adyen in F1", 2, "How a payments peer uses F1",
      t("Airwallex × McLaren: **run the payments, prove it, win clients**"),
      "Source: McLaren Racing modernises cross-border payments with Airwallex (Airwallex case study); SPORTFIVE (team deck: competitor scan, credentials).",
      "Challenge: McLaren Racing operates across 24 race locations with frequent international supplier payments; ~30 manual payments per run, high FX and transfer fees, 2–5 day settlement via banks and SWIFT; the cost cap makes efficiency matter. Solution: implemented in 14 days; batch payouts, approval workflows, faster cross-border transfers; suppliers paid in local currencies; integrated with banking and accounting. Results: 90% of payments within hours, 65% instantly, 110+ countries on local networks, 0.5 day a month saved, £4,000+ a year saved on transaction and FX fees.");
    await photo(s, "airwallex_carbon.jpg", L, 1.95, 2.9, 4.2, "Airwallex branding on McLaren carbon fibre");
    const x0 = L + 3.2, sw = (R - x0 - 0.5) / 3, y = 1.95, h = 4.2;
    const steps = [
      ["1", "Run the payments", "Airwallex pays McLaren's suppliers across 24 race locations.",
        [["Before", "~30 manual international payments per run; 2–5 day settlement"], ["After", "Live in 14 days: batch payouts in local currencies"]]],
      ["2", "Prove it with numbers", "Results McLaren can stand behind.",
        [["90%", "of payments arrive within hours"], ["65%", "arrive instantly"], ["£4,000+", "saved a year on fees"]]],
      ["3", "Use it to win clients", "The partnership becomes Airwallex's enterprise showcase.",
        [["Showcase", "payment solutions shown to enterprises worldwide"], ["Portfolio", "McLaren, Arsenal FC, San Francisco Giants, Essendon FC"]]],
    ];
    const arrow = await icon("FiChevronRight", "0ABF53");
    steps.forEach(([n, head, lead, items], i) => {
      const x = x0 + i * (sw + 0.25);
      const dark = i === 2;
      card(s, x, y, sw, h, dark ? C.text1 : C.background2, "Step card");
      s.addShape(S.OVAL, { x: x + 0.22, y: y + 0.22, w: 0.5, h: 0.5, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
      s.addText(n, { x: x + 0.22, y: y + 0.22, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
      s.addText(head, { x: x + 0.85, y: y + 0.2, w: sw - 1.0, h: 0.55, fontSize: 15, bold: true, color: dark ? C.background1 : C.text1, margin: 0, isTextBox: true, valign: "middle" });
      s.addText(lead, { x: x + 0.22, y: y + 0.88, w: sw - 0.44, h: 0.62, fontSize: 11.5, bold: true, color: dark ? C.accent4 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      items.forEach(([big, lab], k) => {
        const iy = y + 1.6 + k * (items.length === 3 ? 0.83 : 1.2);
        s.addText([{ text: big, options: { bold: true, fontSize: items.length === 3 ? 20 : 13, color: dark ? C.accent1 : C.accent2, breakLine: true } },
          { text: lab, options: { fontSize: 10.5, color: dark ? C.accent4 : C.text2 } }],
        { x: x + 0.22, y: iy, w: sw - 0.44, h: items.length === 3 ? 0.8 : 1.1, margin: 0, isTextBox: true, valign: "top" });
      });
      if (i < 2) s.addImage({ data: arrow, x: x + sw + 0.02, y: y + h / 2 - 0.1, w: 0.21, h: 0.21 });
    });
    card(s, L, 6.3, CW, 0.5, C.accent6, "For Adyen");
    s.addText([{ text: "For Adyen  ", options: { bold: true, color: C.accent2 } },
      { text: "the same play: run a partner's payments, prove it with live data, and use F1 to host and win enterprise clients.", options: { color: C.text1 } }],
    { x: L + 0.25, y: 6.3, w: CW - 0.5, h: 0.5, fontSize: 12.5, margin: 0, isTextBox: true, valign: "middle" });
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
      "Source: Adyen ('Racing | Unified Payments' value chain); Alpine Provisional Rights Overview 2027–2029; Max Verstappen × Adyen proposal; SPORTFIVE team partnership network (Nov 2026).",
      "Integration first, not a logo deal. Top: Adyen's racing value chain, one platform from fan to business bank account. Each step shows what it means on the Alpine and Max routes; Ferrari is still to explore.");
    await fit(s, "adyen_value_chain.png", L, 1.85, 7.4, 1.9, "Adyen unified commerce value chain, from fan to business bank account");
    const tx = 8.35, tw2 = R - tx;
    s.addText([{ text: "One platform, end to end", options: { bold: true, color: C.text1, fontSize: 15, breakLine: true } },
      { text: "Gateway, risk, authentication, processing, acquiring and reconciliation, online and in person.", options: { color: C.text2, fontSize: 12 } }],
    { x: tx, y: 2.05, w: tw2, h: 1.6, margin: 0, isTextBox: true, valign: "top", paraSpaceAfter: 4 });
    const steps = [
      ["FiCreditCard", "Power", "Adyen runs the partner's payments.", "Alpine: team ecommerce store. Max: Verstappen Travel tickets and trailers."],
      ["FiBarChart2", "Prove", "Live data becomes a client case study.", "KPIs: checkout completion, payment performance, conversion."],
      ["FiUsers", "Host", "Hospitality at the centre.", "Alpine: 56 Paddock Club tickets a year. Max: garage tour, track day, plus a hospitality bundle."],
      ["FiShare2", "Connect", "The partner network becomes pipeline.", "Alpine: 49 Team partners, Partner Forum. Max: the Verstappen ecosystem."],
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

  // ================================================================ 04 The routes
  pres.addSection({ title: "The routes" });
  // Routes overview
  {
    const s = content("CONTENT", "The routes", 3, "Overview",
      t("Three routes into F1: **Max Verstappen, Alpine and Ferrari**"),
      "Source: Max Verstappen × Adyen proposal (Oct 2026, for discussion); Alpine F1 Team Provisional Rights Overview 2027–2029; SPORTFIVE team partnership network (Nov 2026).",
      "Max and Alpine come from conversations already under way and have proposals on the table. Ferrari has no proposal yet. The aim is buy-in to F1 first; then expand. Hospitality can be bundled with the Max route (SPORTFIVE, next slides after the rights).");
    const cw = (CW - 0.6) / 3;
    const routes = [
      { n: 1, type: "Driver", name: "Max Verstappen", img: "max_banner.jpg", status: "Proposal: for discussion", fields: [
        ["Opportunity", "Official ambassador; Adyen powers the Verstappen ecosystem; plus hospitality"],
        ["Where Adyen sits", "Verstappen Travel tickets and trailers; Pro Simulation booking"],
        ["Terms", "2027–2030; fee not yet quoted"]] },
      { n: 2, type: "Team", name: "Alpine F1 Team", img: "alpine_engine.jpg", status: "Proposal: for discussion", fields: [
        ["Opportunity", "Exclusive Financial Technology Platform Partner, global"],
        ["Where Adyen sits", "Powers the Team's new ecommerce platform, then hospitality and network"],
        ["Terms", "2027–2029; £10.0M in 2027, +5% a year"]] },
      { n: 3, type: "Team", name: "Scuderia Ferrari", img: "f1_city.jpg", status: "To explore", fields: [
        ["Opportunity", "42 partners with $568bn combined revenue"],
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
      "Transcribed from Max's proposal. The GT3 car position reads 'to discuss (not full car)'. Max's own package excludes Red Bull assets and F1 hospitality; SPORTFIVE can bundle race-weekend hospitality on top (next slides).");
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
        ["b", "Plus: race-weekend hospitality bundle via SPORTFIVE (next pages)"],
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

  // ---------------------------------------------------------------- Route 1 add-on: hospitality bundle (Max only)
  // From SPORTFIVE's 'Adyen – F1 Premium Experiences' deck: an introductory guide, not a quote.
  {
    const s = content("CONTENT_PHOTO", "The routes", 3, "Route 1 · Hospitality bundle",
      t("Max route: **bundle in F1 hospitality** to host Adyen's clients"),
      "Source: Max Verstappen × Adyen proposal (Oct 2026); SPORTFIVE, 'Adyen – F1 Premium Experiences'. Photo: hospitality guests at a Grand Prix (SPORTFIVE).",
      "Max's package includes limited hospitality: an F1 garage tour for 2 VIP guests, a private track day for stakeholders, and 3 × 15-minute paddock meet-and-greets (3 VIP guests each). It excludes Red Bull assets and F1 hospitality. SPORTFIVE is an F1 Experiences Authorised Sales Agent and can bundle race-weekend hospitality on top. The next three slides are an introductory guide: example races, packages and a sample programme. The goal is Adyen's feedback, then a bespoke programme. Hospitality is bundled with the Max route only.");
    await photo(s, "hosp_terrace_guests.jpg", 0, 0, 4.85, H, "Hospitality guests at a Grand Prix");
    const x = 5.35, w = R - x;
    label(s, "In Max's package today", x, 1.95, 3.6);
    ["Garage tour for 2 VIP guests", "Private track day", "3 paddock meet-and-greets"].forEach((it, i) => {
      const bw = (w - 0.3) / 3, bx = x + i * (bw + 0.15);
      s.addShape(S.ROUNDED_RECTANGLE, { x: bx, y: 2.28, w: bw, h: 0.48, rectRadius: 0.24, fill: { color: C.background2 }, line: { color: C.accent4, width: 0.75 } });
      s.addText(it, { x: bx, y: 2.28, w: bw, h: 0.48, fontSize: 10.5, bold: true, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true });
    });
    label(s, "Add with SPORTFIVE: race-weekend hospitality", x, 3.0, w, C.accent2);
    const rows = [
      ["FiStar", "A premium setting", "VIP-level experiences few other sports can match, at the Grands Prix Adyen chooses"],
      ["FiUsers", "Time to do business", "Private spaces and up to three full days to host clients, merchants and prospects"],
      ["FiGift", "Incentive and reward", "Reward top clients and teams, and build lasting relationships"],
    ];
    for (const [i, [ic, head, body]] of rows.entries()) {
      const ry = 3.35 + i * 0.68;
      await iconDot(s, ic, x, ry, 0.48);
      s.addText([{ text: head, options: { bold: true, color: C.text1, fontSize: 13, breakLine: true } }, { text: body, options: { color: C.text2, fontSize: 11 } }],
        { x: x + 0.65, y: ry - 0.04, w: w - 0.65, h: 0.62, margin: 0, isTextBox: true, valign: "top" });
    }
    card(s, x, 5.5, w, 0.62, C.text1, "Credentials strip");
    const cred = [["20+ years", "of premium hospitality"], ["30,000+", "guests a year"], ["Authorised", "F1 Experiences sales agent"]];
    const cw3 = w / 3;
    cred.forEach(([big, lab], i) => s.addText([{ text: big + "  ", options: { bold: true, color: C.accent1, fontSize: 14 } }, { text: lab, options: { color: C.background1, fontSize: 10 } }],
      { x: x + 0.2 + i * cw3, y: 5.5, w: cw3 - 0.25, h: 0.62, margin: 0, isTextBox: true, valign: "middle" }));
    card(s, x, 6.2, w, 0.62, C.accent6, "Starting point");
    s.addText([{ text: "A starting point, not a quote  ", options: { bold: true, color: C.accent2 } },
      { text: "the next pages show example races, packages and a programme. With Adyen's feedback, we build it bespoke.", options: { color: C.text1 } }],
    { x: x + 0.2, y: 6.2, w: w - 0.4, h: 0.62, fontSize: 11, margin: 0, isTextBox: true, valign: "middle" });
  }
  {
    const s = content("CONTENT", "The routes", 3, "Route 1 · Hospitality bundle",
      t("24 races in 2027: **choose where to host**"),
      "Source: 2027 F1 calendar as shown in SPORTFIVE's 'Adyen – F1 Premium Experiences' (not independently confirmed). Adyen office cities: the footprint slide.",
      "Green: races used as examples on the next two slides (Miami, Silverstone, Singapore, Austin). Dot: a race in a city where Adyen has an office (Madrid, Mexico City, Shanghai, Singapore, São Paulo). Order as shown in the source calendar.");
    const colW = (CW - 0.5) / 3, rh = 0.5, y0 = 1.9;
    CALENDAR.forEach(([d, country, city], i) => {
      const col = Math.floor(i / 8), row = i % 8;
      const x = L + col * (colW + 0.25), y = y0 + row * (rh + 0.06);
      const ex = EXAMPLE_RACES.includes(country);
      s.addShape(S.ROUNDED_RECTANGLE, { x, y, w: colW, h: rh, rectRadius: 0.06, fill: { color: ex ? C.text1 : C.background2 }, line: { color: ex ? C.text1 : C.background2, width: 0 } });
      s.addText(d, { x: x + 0.15, y, w: 1.25, h: rh, fontSize: 10, bold: true, color: ex ? C.accent1 : C.accent2, margin: 0, isTextBox: true, valign: "middle" });
      s.addText([{ text: country === city ? country : country, options: { bold: true, color: ex ? C.background1 : C.text1, fontSize: 12, breakLine: country !== city } },
        ...(country !== city ? [{ text: city, options: { color: ex ? C.accent4 : C.text2, fontSize: 9.5 } }] : [])],
      { x: x + 1.4, y, w: colW - 1.85, h: rh, margin: 0, isTextBox: true, valign: "middle" });
      if (ADYEN_OFFICE_RACES.includes(country))
        s.addShape(S.OVAL, { x: x + colW - 0.33, y: y + rh / 2 - 0.08, w: 0.16, h: 0.16, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
    });
    const ly = y0 + 8 * (rh + 0.06) + 0.06;
    s.addShape(S.ROUNDED_RECTANGLE, { x: L, y: ly + 0.04, w: 0.3, h: 0.2, rectRadius: 0.03, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
    s.addText("Example race in this guide", { x: L + 0.4, y: ly, w: 2.6, h: 0.28, fontSize: 10, color: C.text2, margin: 0, isTextBox: true, valign: "middle" });
    s.addShape(S.OVAL, { x: L + 3.1, y: ly + 0.06, w: 0.16, h: 0.16, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
    s.addText("Race in a city with an Adyen office", { x: L + 3.35, y: ly, w: 3.2, h: 0.28, fontSize: 10, color: C.text2, margin: 0, isTextBox: true, valign: "middle" });
  }
  {
    const s = content("CONTENT", "The routes", 3, "Route 1 · Hospitality bundle",
      t("Example packages: from **shared clubs to private suites**"),
      "Source: SPORTFIVE, 'Adyen – F1 Premium Experiences' (race overviews). Prices per person unless a group size is shown; content differs GP to GP.",
      "Three of the race overviews in SPORTFIVE's deck, one per region Adyen named in its brief. Green tag: packages with Oracle Red Bull Racing access, the closest link to Max. Miami Red Bull Energy Station also lists Q&As with Visa Cash App Racing Bulls drivers, Red Bull athletes and F1 Team Principals, and Playseat simulators. Singapore Red Bull Paddock also includes guided daily pit-lane walks. Full race overviews (Miami, Monaco, Silverstone, Monza, Madrid, Singapore, Austin, Las Vegas) are in SPORTFIVE's deck.");
    const cw = (CW - 0.5) / 3, y = 1.85;
    for (const [i, r] of PACKAGES.entries()) {
      const x = L + i * (cw + 0.25);
      s.addShape(S.ROUNDED_RECTANGLE, { x, y, w: cw, h: 0.66, rectRadius: 0.06, fill: { color: C.text1 }, line: { color: C.text1, width: 0 } });
      s.addText([{ text: r.race, options: { bold: true, color: C.background1, fontSize: 16, breakLine: true } }, { text: r.when, options: { color: C.accent4, fontSize: 9.5 } }],
        { x: x + 0.2, y, w: cw - 1.7, h: 0.66, margin: 0, isTextBox: true, valign: "middle" });
      s.addText(r.region.toUpperCase(), { x: x + cw - 1.6, y, w: 1.45, h: 0.66, fontSize: 8.5, bold: true, color: C.accent1, align: "right", charSpacing: 1, margin: 0, isTextBox: true, valign: "middle" });
      r.pk.forEach(([name, scope, hl, price, unit, rb], k) => {
        const py = y + 0.76 + k * 1.02, ph2 = 0.94;
        card(s, x, py, cw, ph2, rb ? C.accent6 : C.background2, "Package");
        if (rb) s.addShape(S.RECTANGLE, { x, y: py, w: 0.07, h: ph2, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
        s.addText([{ text: name, options: { bold: true, color: C.text1, fontSize: 11.5 } }, { text: "  " + scope, options: { color: C.text2, fontSize: 9 } }],
          { x: x + 0.17, y: py + 0.05, w: cw - 1.45, h: 0.32, margin: 0, isTextBox: true, valign: "middle" });
        s.addText([{ text: "from", options: { color: C.text2, fontSize: 8, breakLine: true } }, { text: price, options: { bold: true, color: C.accent2, fontSize: 14 } }],
          { x: x + cw - 1.3, y: py + 0.04, w: 1.15, h: 0.5, margin: 0, isTextBox: true, valign: "top", align: "right" });
        s.addText(hl, { x: x + 0.17, y: py + 0.37, w: cw - 1.5, h: 0.55, fontSize: 9, color: C.text2, margin: 0, isTextBox: true, valign: "top" });
        s.addText(unit, { x: x + cw - 1.45, y: py + 0.53, w: 1.3, h: 0.4, fontSize: 8, color: C.text2, margin: 0, isTextBox: true, valign: "top", align: "right" });
      });
    }
    s.addShape(S.RECTANGLE, { x: L, y: 6.7, w: 0.07, h: 0.2, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 } });
    s.addText("Green: packages with Oracle Red Bull Racing access, the closest link to Max.  Starting prices in US$; indicative and subject to availability.",
      { x: L + 0.17, y: 6.66, w: CW - 0.2, h: 0.28, fontSize: 9.5, color: C.text2, margin: 0, isTextBox: true, valign: "middle" });
  }
  {
    const s = content("CONTENT", "The routes", 3, "Route 1 · Hospitality bundle",
      t("Example programme: **four days in Austin** around the US Grand Prix"),
      "Source: SPORTFIVE, 'Adyen – F1 Premium Experiences' (example programming, Formula One – Austin 2027, October, date TBC). Photos: SPORTFIVE.",
      "An example of how SPORTFIVE builds a full programme around one race. Every element is bespoke and would be designed with Adyen. Delivery: SPORTFIVE is a licensed IATA travel agent with close relations to major airlines; owned inventory and long-standing relationships with high-end hotel chains; a branded digital platform for ticket distribution, guest data, invitations and itineraries; and a network of local partners for staffing, suppliers and logistics.");
    const cw = (CW - 0.6) / 4, y = 1.9, ih = 1.55, h = 3.95;
    for (const [i, [day, head, img, alt, items]] of AUSTIN.entries()) {
      const x = L + i * (cw + 0.2);
      const race = i === 2;
      card(s, x, y, cw, h, race ? C.text1 : C.background2, "Day card");
      await photo(s, img, x, y, cw, ih, alt);
      s.addText([{ text: day.toUpperCase(), options: { bold: true, color: C.accent1, fontSize: 10, charSpacing: 1, breakLine: true } },
        { text: head, options: { bold: true, color: race ? C.background1 : C.text1, fontSize: 14 } }],
      { x: x + 0.2, y: y + ih + 0.12, w: cw - 0.4, h: 0.7, margin: 0, isTextBox: true, valign: "top" });
      s.addText(items.map((it, k) => ({ text: it, options: { bullet: { indent: 10 }, breakLine: k < items.length - 1, paraSpaceAfter: 3 } })),
        { x: x + 0.2, y: y + ih + 0.85, w: cw - 0.4, h: h - ih - 0.95, fontSize: 10, color: race ? C.accent4 : C.text2, margin: 0, isTextBox: true, valign: "top" });
    }
    card(s, L, 6.0, CW, 0.82, C.text1, "Delivery strip");
    s.addText("SPORTFIVE RUNS IT END TO END", { x: L + 0.25, y: 6.0, w: 2.2, h: 0.82, fontSize: 10, bold: true, color: C.accent1, charSpacing: 1, margin: 0, isTextBox: true, valign: "middle" });
    const del = [["Travel", "licensed IATA travel agent"], ["Hotels", "owned inventory, top hotel chains"], ["Guests", "branded digital invitations and itineraries"], ["On site", "local partners, staffing and logistics"]];
    const dw = (CW - 2.6) / 4;
    del.forEach(([h2, lab], k) => s.addText([{ text: h2, options: { bold: true, color: C.background1, fontSize: 12, breakLine: true } }, { text: lab, options: { color: C.accent4, fontSize: 9.5 } }],
      { x: L + 2.5 + k * dw, y: 6.0, w: dw - 0.15, h: 0.82, margin: 0, isTextBox: true, valign: "middle" }));
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
      t("Scuderia Ferrari: 42 partners, and **the most fans in financial services**"),
      "Source: SPORTFIVE team partnership network (Nov 2026); Global Web Index (2026), North America and Europe.",
      "No Ferrari proposal yet. Whether to open a conversation is a next step. Partner data: 42 partners, 60% public; $568bn combined 2025 partner revenue (#6 of 11 teams); 6 partners in Tier 1 ($200bn+). Fans: 1.80M Ferrari fans work in financial services, the largest pool of any team (index 136.2).");
    await photo(s, "f1_city.jpg", L, 1.95, 4.3, 4.7, "F1 car at speed");
    const x = L + 4.65, w = R - x;
    const stats = [["1.80M", "Ferrari fans working in financial services: the most of any team"], ["42", "partners, 60% of them public companies"],
      ["$568bn", "combined revenue of Ferrari's partners in 2025"], ["6", "partners worth $200bn+ each"]];
    const tw = (w - 0.25) / 2, th = 1.35;
    stats.forEach(([big, lab], i) => {
      const tx = x + (i % 2) * (tw + 0.25), ty = 1.95 + Math.floor(i / 2) * (th + 0.2);
      card(s, tx, ty, tw, th, i === 0 ? C.text1 : C.background2);
      s.addText(big, { x: tx + 0.25, y: ty + 0.15, w: tw - 0.5, h: 0.6, fontSize: 30, bold: true, color: i === 0 ? C.accent1 : C.text1, margin: 0, isTextBox: true, valign: "top" });
      s.addText(lab, { x: tx + 0.25, y: ty + 0.78, w: tw - 0.5, h: 0.5, fontSize: 11, color: i === 0 ? C.accent4 : C.text2, margin: 0, isTextBox: true, valign: "top" });
    });
    s.addText([{ text: "Top partners  ", options: { bold: true, color: C.text1 } }, { text: "Shell $267bn · IBM $68bn · HP $56bn (2025 revenue)", options: { color: C.text2 } }],
      { x, y: 4.95, w, h: 0.35, fontSize: 13, margin: 0, isTextBox: true, valign: "middle" });
    card(s, x, 5.45, w, 1.2, C.background2, "Status card");
    s.addText([{ text: "Status  ", options: { bold: true, color: C.accent2, fontSize: 13 } },
      { text: "No proposal yet: to explore. Whether to open a conversation with Ferrari is one of the next steps.", options: { color: C.text1, fontSize: 13 } }],
    { x: x + 0.3, y: 5.45, w: w - 0.6, h: 1.2, margin: 0, isTextBox: true, valign: "middle" });
  }

  // ================================================================ 05 Next steps
  pres.addSection({ title: "Next steps" });
  {
    const s = content("CONTENT", "Next steps", 4, "Next steps",
      t("Next steps: **from review to launch**"),
      "Source: SPORTFIVE. Review date: team deck.",
      "Six steps, in order. The first is the Chairman's review of the Max and Alpine proposals; Ferrari is a decision in step 4. Visuals: Adyen mock-ups from the two proposals on the table (Max's team; Alpine).");
    const vx = 8.15, vw = R - vx, vh = 2.3;
    await photo(s, "max_adyen_cap_band.jpg", vx, 1.95, vw, vh, "Max Verstappen in an Adyen-branded cap (mock-up by Max Verstappen's team)");
    await photo(s, "alpine_engine.jpg", vx, 1.95 + vh + 0.15, vw, vh, "Alpine car with Adyen branding on the engine cover (mock-up)");
    [["Max Verstappen × Adyen", 1.95], ["Alpine F1 Team × Adyen", 1.95 + vh + 0.15]].forEach(([cap, cy]) => {
      s.addShape(S.RECTANGLE, { x: vx, y: cy + vh - 0.42, w: vw, h: 0.42, fill: { color: C.text1, transparency: 15 }, line: { color: C.text1, width: 0 } });
      s.addText([{ text: cap, options: { bold: true, color: C.background1 } }, { text: "   mock-up from the proposal", options: { color: C.accent4 } }],
        { x: vx + 0.2, y: cy + vh - 0.42, w: vw - 0.4, h: 0.42, fontSize: 10.5, margin: 0, isTextBox: true, valign: "middle" });
    });
    const steps = [["Chairman reviews the Max and Alpine proposals", "Week of 9 November 2026"], ["Gather feedback, including on the hospitality bundle", null],
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
      "Keep this slide: it answers 'where does that number come from?' in the room. Backup slides (hidden) follow: fans in finance, Adyen markets, competitors in sport, route assessment, Ferrari detail.");
    const src = [
      ["GWI", "Global F1 audience 2022–2026; F1 audience by Adyen office market; sport affinity indices; team fans working in financial services (2026); Alpine fan audience (GWI Core, Q3 2025–Q2 2026)."],
      ["GlobalData", "F1 sponsorship 2020–2025 (new deals only); brands involved in F1 and their combined revenue (2026)."],
      ["Kantar", "BrandZ 2026 Most Valuable Global Brands; Strong Brands Portfolio 2006–2026; IBM and American Express spotlights; Kantar × Google 2026."],
      ["SPORTFIVE", "Team partnership network (Nov 2026): partner revenue, counts, market-cap tiers. 'Adyen – F1 Premium Experiences': 2027 calendar, packages, Austin programme, CommScope and Century Financial references. Competitor scan (not exhaustive); Businessolver × Alpine case; Airwallex × McLaren credentials."],
      ["Rights holders", "Alpine Formula One Team, Provisional Rights Overview 2027–2029 (not legally binding). Max Verstappen × Adyen proposal, October 2026 (for discussion)."],
      ["Adyen", "Office locations; partnership brief; 'Racing | Unified Payments' imagery and value chain."],
      ["Calculated", "Counts and sums from the sources above: 24 races, 28 offices, 34.4M fans, 56 tickets, competitor property counts, '% above next-best sport', market-cap tier shading."],
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
        "Garage tour, track day, paddock meet-and-greets; hospitality bundle via SPORTFIVE", "Max's personal business ecosystem; no team partner network",
        "Top follower markets: USA, Brazil, Netherlands, Mexico, UK, Germany", "Non-exclusive ambassador rights"],
      alp: ["Powers agreed parts of the Team's new ecommerce platform", "Checkout, rewards and race-week venue payments; KPIs proposed",
        "56 Paddock Club tickets a year, Enstone events, near-track dinners", "Introductions to 49 Team partners; One Platform Partner Forum",
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
