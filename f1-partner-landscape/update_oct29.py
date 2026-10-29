"""Second pass (29 Oct 2026): additions, renames, 2026 announcement months and 2027+ signings
found by the roster verification, applied on top of data.py. Writes data.json.

Each partner may now carry `starts`: the year a signed partnership begins (2027 = not yet active).
"""
import json
import sys

import data

T = {k: [list(p) for p in v] for k, v in data.T.items()}
SRC = dict(data.SRC)

def idx(team, name):
    for i, p in enumerate(T[team]):
        if p[0] == name:
            return i
    raise KeyError((team, name))

def add(team, name, row, sector, tier, new=None, starts=None):
    assert all(p[0] != name for p in T[team]), (team, name)
    T[team].append([name, row, sector, tier, new, starts])

def rename(team, old, new_name):
    T[team][idx(team, old)][0] = new_name

def mark(team, month, *names):
    for n in names:
        T[team][idx(team, n)][4] = month

for team in T:
    for p in T[team]:
        if len(p) == 5:
            p.append(None)

# ---------------------------------------------------------------- Formula 1
add("f1", "Fanatec", 3, "O", "F1 Sim Racing Official Sponsor / licensee")
add("f1", "ALT Sports Data", 3, "O", "Official Betting Data Supplier")
add("f1", "LEGO", 3, "O", "Licensing partner")
add("f1", "Mattel (Hot Wheels)", 3, "O", "Licensing partner")
add("f1", "Disney", 3, "O", "Licensing partner (extended to 2028)")
add("f1", "Leica", 3, "O", "Licensing partner", new="Oct")
mark("f1", "Mar", "Betway"); mark("f1", "Apr", "FanDuel"); mark("f1", "Jun", "Fever"); mark("f1", "Jul", "Flexjet")
SRC["f1"] = ("formula1.com partner roster (official, read 29 Oct 2026) and RTR Sports (6 Oct 2026); licensing partners from "
             "F1 and partner announcements")

# ---------------------------------------------------------------- Mercedes
add("mercedes", "Zuma", 2, "O", "Lifestyle & Dining Curator", new="Jan")
mark("mercedes", "Jan", "Nu"); mark("mercedes", "Jul", "Vercel")
SRC["mercedes"] += "; Zuma (team release, 23 Jan 2026)"

# ---------------------------------------------------------------- Red Bull
rename("redbull", "Mobil 1", "ExxonMobil (Mobil 1, Mobil)")
mark("redbull", "Jan", "CLEAR"); mark("redbull", "Mar", "Indeed")

# ---------------------------------------------------------------- Ferrari
add("ferrari", "Rakuten", 2, "O", "Team Partner from 1 Jan 2027", new="Sep", starts=2027)
mark("ferrari", "Jan", "WHOOP"); mark("ferrari", "Jun", "SkinCeuticals")
SRC["ferrari"] += "; Rakuten (Rakuten release, 17 Sep 2026)"

# ---------------------------------------------------------------- McLaren
rename("mclaren", "Google", "Google (Android, Chrome, Gemini, Google Cloud)")
rename("mclaren", "Cisco", "Cisco (Webex, Splunk)")
rename("mclaren", "Stanley Black & Decker", "Stanley Black & Decker (DEWALT)")
add("mclaren", "Edward Jones", 2, "FS", "Official Private Wealth Management Partner", new="Sep")
add("mclaren", "P&G (Head & Shoulders, Oral-B)", 2, "O", "Partner (Asia-Pacific)", new="Oct")
add("mclaren", "Pure Electric", 2, "O", "Partner")
add("mclaren", "Stratasys", 3, "O", "Official Supplier of 3D Printing Solutions")
add("mclaren", "Topps", 3, "O", "Official trading-card licensee", new="Apr")
add("mclaren", "Commercial Bank", 3, "FS", "Official Race Partner, Qatar GP (2025-2027)")
mark("mclaren", "Apr", "Liquid I.V."); mark("mclaren", "May", "Intel")
SRC["mclaren"] = ("f1salaries.com/sponsors/mclaren (30 Sep 2026), checked against McLaren's partner list of 20 Oct 2026; "
                  "plus AbbVie, Edward Jones, P&G, Topps, Commercial Bank (team and partner releases)")

# ---------------------------------------------------------------- Aston Martin
add("astonmartin", "Meccano", 3, "O", "Licensing partner", new="Jan")
add("astonmartin", "Memento Exclusives", 3, "O", "Licensing partner (extended Apr 2026)")
add("astonmartin", "Smythson", 3, "O", "Licensing collaboration", new="May")
add("astonmartin", "Defected Records", 3, "O", "Collaboration", new="Aug")
add("astonmartin", "Padeltek", 3, "O", "Collaboration (expands 2027)", new="Oct")
add("astonmartin", "Globe-Trotter", 3, "O", "Global Luxury Luggage Partner (per brand)")
mark("astonmartin", "Jan", "Celsius"); mark("astonmartin", "Feb", "Breitling", "Cognition", "Eight Sleep")
mark("astonmartin", "Mar", "Cohere"); mark("astonmartin", "May", "AQUAME"); mark("astonmartin", "Jun", "Zscaler")
mark("astonmartin", "Oct", "BK8 News", "BOXBOX")
SRC["astonmartin"] += "; licensing and collaboration deals from the team's announcements (Jan-Oct 2026)"

# ---------------------------------------------------------------- Racing Bulls
rename("vcarb", "Mobil 1", "ExxonMobil (Mobil 1, Esso, Mobil)")
add("vcarb", "Cefla", 3, "O", "Official Supplier / Sustainability Partner")
mark("vcarb", "Mar", "Octave"); mark("vcarb", "May", "Barilla", "Floyd"); mark("vcarb", "Jun", "Salesforce")
mark("vcarb", "Oct", "ThreatLocker", "Introl")
SRC["vcarb"] += "; Cefla (team release, 25 Feb 2026)"

# ---------------------------------------------------------------- Audi
rename("audi", "Gillette (P&G)", "P&G (Gillette, Braun, Venus)")
add("audi", "Elastic", 3, "O", "Official Race Partner (US GP 2026); Official Supplier from 2027", new="Oct")
add("audi", "Memento Exclusives", 3, "O", "Licensing partner", new="Apr")
T["audi"][idx("audi", "Libertex")][4] = None  # continued from the Sauber era: a renewal, not a new deal
mark("audi", "Jan", "NinjaOne", "Hyatt", "P&G (Gillette, Braun, Venus)", "Piquadro")
mark("audi", "Feb", "ic! berlin"); mark("audi", "Mar", "Mammoet", "Glasurit"); mark("audi", "May", "Specialized")
mark("audi", "Oct", "Öhlins")
SRC["audi"] += "; Elastic and Memento Exclusives (team and partner releases)"

# ---------------------------------------------------------------- Cadillac
add("cadillac", "Memento Exclusives", 3, "O", "Licensing partner", new="Jun")
SRC["cadillac"] += "; Memento Exclusives (24 Jun 2026)"

# ---------------------------------------------------------------- Alpine, Williams, Haas
def update_awh():
    # Alpine
    add("alpine", "Gucci", 1, "O", "Title Partner from 2027 (Gucci Racing Alpine F1 Team)", new="May", starts=2027)
    add("alpine", "Brioni", 2, "O", "Formalwear partner (team release; not on partner page)", new="Apr")
    mark("alpine", "Jan", "IndraMind"); mark("alpine", "May", "Skip"); mark("alpine", "Oct", "Apex Ultra")
    SRC["alpine"] += "; Gucci (formula1.com, 27 May 2026) and Brioni (team release, 28 Apr 2026)"
    # Williams
    add("williams", "Klaviyo", 2, "O", "Official B2C CRM Partner from 2027", new="Oct", starts=2027)
    add("williams", "Marvel", 3, "O", "Season-long collaboration", new="Apr")
    add("williams", "Dandadan (MBS)", 3, "O", "Anime collaboration (Sector Zero)", new="Apr")
    add("williams", "Racing Camp", 3, "O", "Licensed camp collaboration from summer 2027", new="Oct", starts=2027)
    mark("williams", "Jan", "Nuveen", "BNY", "Sparco", "Wilkinson Sword")
    mark("williams", "Feb", "Claude", "Barclays", "Estrella Galicia", "M&S")
    SRC["williams"] += "; Klaviyo, Marvel, Dandadan, Racing Camp (team releases, Apr-Oct 2026)"
    # Haas
    rename("haas", "IC Markets", "IC (IC Markets)")
    add("haas", "TENEX.AI", 2, "O", "Official Partner (cybersecurity)", new="Oct")
    add("haas", "Dynamo Capital", 2, "FS", "Partner (North America)", new="Oct")
    add("haas", "Memento Exclusives", 3, "O", "Global licensing partner", new="Oct")
    add("haas", "TOHO (Godzilla)", 3, "O", "Season-long collaboration", new="Mar")
    T["haas"][idx("haas", "RUCKUS Networks")][4] = None  # expansion of an existing deal, not new
    mark("haas", "Jan", "Fix Network"); mark("haas", "Feb", "Singha"); mark("haas", "Apr", "D.Energy")
    mark("haas", "Jun", "Emburse", "NeverMile"); mark("haas", "Jul", "Exein")
    SRC["haas"] += "; TENEX.AI, Dynamo Capital, Memento Exclusives, TOHO (team releases, Mar-Oct 2026)"


# Brands checked and deliberately left out, with the reason (shown on the notes slide)
EXCLUDED = [
    ("Not active / not confirmed for 2026",
     "AWS and MAHLE (Ferrari: absent from 2026 lists, no exit announced); ONEflight International (McLaren: suspended operations "
     "Sep 2026, removed from McLaren's partner list); BlockDAG and MNTN (Alpine: not in the 2026 grid, BlockDAG page removed); "
     "Gainbridge and UKG (Cadillac: no official role found); Playseat, DK (F1); CDW (Red Bull); Yugo (Racing Bulls); "
     "Circle8 (Aston Martin); SEGA (McLaren); UNDONE, BW Scores (Williams)"),
    ("Outside scope",
     "Owners (Audi, Red Bull, GM/TWG); race-promoter title deals (e.g. Gulf Air, Bahrain GP); power-unit supply; agencies "
     "(Brandand, Excel Sports); one-off activations (Apple TV, Peloton, Resorts World Sentosa, Pantone); F1 Academy-only "
     "(e.g. Sephora, NEOM, Unity) and esports-only deals; driver personal deals"),
]


if __name__ == "__main__":
    update_awh()
    out = {"teams": [], "sources": SRC, "excluded": EXCLUDED}
    for key, name, group in data.TEAMS:
        rows = T[key]
        names = [r[0] for r in rows]
        assert len(names) == len(set(names)), key
        out["teams"].append({"key": key, "name": name, "group": group, "partners": [
            {"name": n, "row": r, "sector": s, "tier": t, "new": nw, "starts": st} for n, r, s, t, nw, st in rows]})
    json.dump(out, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
    for t in out["teams"]:
        p = t["partners"]
        cur = [x for x in p if not x["starts"]]
        print(f'{t["name"]:28} current {len(cur):3}  from-2027 {len(p) - len(cur)}  new-2026 {sum(1 for x in p if x["new"])}')
