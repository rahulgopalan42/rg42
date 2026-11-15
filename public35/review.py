"""Manual review decisions for the listed-company database (read by build.py).
F1: what to do with each company where a research pass reported a possible Formula 1 link.
     'exclude' = a current F1 partner, or the parent / subsidiary / brand owner of one -> not listed
     'note'    = not a partner and not a parent or subsidiary, but close enough to check before outreach (kept, flagged)
     'clear'   = the reported link does not hold (kept, no flag)
   A reported link with no decision here is excluded.
DROP: companies taken out for another reason.   CLEAR_FLAG: corporate-status flags from the research pass that do not hold."""
F1 = {
 'DELL': ('exclude', 'Dell Technologies is a current F1 team partner'),
 'PRESIGHT.AE': ('exclude', 'part of G42, a current F1 partner'),
 'YOU': ('clear', 'the Red Bull Racing partner "Clear" is the Unilever haircare brand, not CLEAR Secure'),
 'SHF.DE': ('exclude', 'being taken private by Carlyle, a Red Bull Racing partner'),
 'WKEY': ('exclude', 'parent of SEALSQ, a current F1 partner'),
 'CTSH': ('exclude', 'Cognizant is a current F1 team partner'),
 '7202.SR': ('exclude', 'subsidiary of stc, a current F1 partner'),
 'HEXT.NS': ('exclude', 'controlled by Carlyle, a Red Bull Racing partner'),
 'CRCL': ('exclude', 'Circle is a current F1 partner'),
 'BSBR': ('exclude', 'subsidiary of Santander, a current F1 partner'),
 'BSAC': ('exclude', 'subsidiary of Santander, a current F1 partner'),
 'MRSH': ('exclude', 'Marsh is a current F1 partner'),
 'OPAP.AT': ('exclude', 'subsidiary of Allwyn, a current F1 partner'),
 '2282.HK': ('exclude', 'subsidiary of MGM Resorts, a current F1 partner'),
 '9984.T': ('exclude', 'parent of Arm, a current F1 partner'),
 'AMX': ('exclude', 'America Movil (Claro) is a current F1 partner'),
 'TA1.F': ('exclude', 'subsidiary of America Movil (Claro), a current F1 partner'),
 'STC.KW': ('exclude', 'subsidiary of stc, a current F1 partner'),
 'EIN.DE': ('exclude', 'Einhell is a current F1 team partner'),
 'FROTO.IS': ('exclude', 'Ford joint venture; Ford is in F1 through Red Bull Ford Powertrains'),
 'PHIN': ('exclude', 'owner of the Delphi brand, a current F1 team partner'),
 'IMO': ('exclude', 'majority-owned by ExxonMobil (Mobil 1, Esso Synergy)'),
 '010950.KS': ('exclude', 'majority-owned by Aramco, a Formula 1 global partner'),
 '2223.SR': ('exclude', 'subsidiary of Aramco, a Formula 1 global partner'),
 '2587.T': ('exclude', 'Suntory group, owner of Jim Beam (Cadillac partner)'),
 'UBL.NS': ('exclude', 'majority-owned by Heineken, a Formula 1 global partner'),
 'MCD': ('exclude', "McDonald's brand is in F1 through Arcos Dorados"),
 'DOC.VI': ('exclude', 'long-standing Formula 1 Paddock Club catering supplier'),
 'ENR': ('exclude', 'owner of Armor All, a current F1 team partner'),
 'SFL.MI': ('exclude', 'makes BOSS and HUGO eyewear under licence; HUGO Eyewear is a Racing Bulls partner'),
 'SOMS.OM': ('exclude', 'majority-owned by Shell, a Ferrari partner'),
 'CDI.PA': ('exclude', 'controlling holding company of LVMH, a Formula 1 global partner'),
 'COF': ('note', 'A research pass recalled a possible F1 team link for Capital One; it is not on the 2025-26 roster. Confirm before outreach.'),
 'KLAR': ('note', 'A research pass recalled a possible F1 team link for Klarna; it is not on the 2025-26 roster. Confirm before outreach.'),
 'VAC': ('note', 'Uses Marriott brands under licence (not a Marriott subsidiary); Marriott Bonvoy is a Mercedes partner. Check for category conflict.'),
 'HGV': ('note', 'Uses the Hilton brand under licence (not a Hilton subsidiary); Hilton is a McLaren partner. Check for category conflict.'),
 'CSAN': ('note', 'Its Raizen joint venture with Shell sells Shell-branded fuel in Brazil; Shell is a Ferrari partner. Check for category conflict.'),
 'MOH.AT': ('note', 'Runs Shell-branded stations in Greece under licence; Shell is a Ferrari partner. Check for category conflict.'),
 'ELPE.AT': ('note', 'Runs BP-branded stations in Greece under licence; BP / Castrol are F1 partners. Check for category conflict.'),
 'VEA.AX': ('note', 'Holds the Shell brand licence in Australia; Shell is a Ferrari partner. Check for category conflict.'),
 'AAPL': ('note', 'Apple TV is the US broadcast partner of Formula 1 from 2026 (media rights, not a sponsorship). Not on the partner roster.'),
 'VBL.NS': ('note', 'PepsiCo franchise bottler (not a PepsiCo subsidiary); PepsiCo is a Formula 1 global partner. Check for category conflict.'),
 'COTY': ('note', 'Makes BOSS and HUGO fragrances under licence; HUGO BOSS is an F1 team partner. Check for category conflict.'),
 'MOV': ('note', 'Makes Tommy Hilfiger watches under licence; Tommy Hilfiger is a Cadillac partner. Check for category conflict.'),
 '9914.TW': ('note', 'Holds a minority stake in Specialized, an F1 team partner. Not a parent company.'),
 'LVS': ('clear', 'The Venetian Resort Las Vegas (an F1 partner) was sold by Las Vegas Sands in 2022'),
 'BYD': ('clear', 'Boyd Gaming is not the owner of FanDuel (Flutter is)'),
 'HYUNDAI.NS': ('clear', 'Hyundai is not on the roster'),
 'BOSCHLTD.NS': ('clear', 'Bosch is not on the partner roster'),
 'NXE': ('clear', 'the roster partner is NexGen Cloud (nexgencloud.com), not NexGen Energy'),
 '6110.HK': ('clear', 'retailer of partner brands only'),
 'WOSG.L': ('clear', 'retailer of partner brands only'),
}
DROP = {
 'WBD': 'acquired by Paramount Skydance (an F1 partner) and delisted in Oct 2026',
 'DAY': 'taken private by Thoma Bravo', 'SHCO': 'taken private by MCR Hotels', 'YAHSAT.AE': 'merged into Space42', '7205.T': 'merged into Archion (no longer separately listed)',
 '096775.KS': 'preferred share line of SK Innovation (ordinary shares listed separately)', 'ASGN': 'old ticker of the same company (now Everforth, EFOR)',
 'SCVL': 'old ticker of the same company (now Shoe Station Group, SHOE)', 'ORDS.AE': 'second listing of Ooredoo (ORDS.QA kept)', '8301.T': 'central bank',
 'GLOP-PA': 'preferred units, not an operating listing', 'OZON.ME': 'Russian market', 'FIVE.ME': 'Russian market', 'OZON': 'Russian market', 'QIWI': 'Russian market',
 '688256.SS': 'on the US Entity List', '688795.SS': 'on the US Entity List', '002415.SZ': 'on the US Entity List',
}
CLEAR_FLAG = {'AMLAK.AE', 'STC', 'SPCX'}          # still listed / the name is not in doubt
FIX = {'SPCX': {'hq': 'Starbase (Texas), United States', 'conf': 'medium'}}          # corrections to profile fields
NOTE = {
 'BUD': 'Michelob Ultra (AB InBev) announced a North America partnership with Williams Racing in 2024; it is not on the Williams partner page in Nov 2026. Confirm before outreach.',                                                                             # extra F1-proximity notes (kept, flagged for checking)
 'WYNN': 'Wynn Las Vegas was a founding partner of the Las Vegas Grand Prix in 2023; not on the current roster. Confirm status before outreach.',
 'CZR': 'Caesars Entertainment was a founding partner of the Las Vegas Grand Prix in 2023; not on the current roster. Confirm status before outreach.',
 'PUIG.MC': 'Charlotte Tilbury (a Puig brand) is an F1 Academy partner; not a Formula 1 championship or team partner.',
 'TCS.NS': 'Sister company Tata Communications is a Formula 1 partner; TCS itself is not on the roster.',
}
WEB = {'LVS': 'none', '4755.T': 'current', 'ENT.L': 'unclear', 'BUD': 'unclear'}          # overrides to the web-check status, sym -> 'current' | 'past' | 'related' | 'none' | 'unclear'
ROSTER_EXTRA = {     # found when the official team partner pages were re-read on 15 Nov 2026, and subsidiaries of sponsors found by the web check
 'BBD': 'Bradesco is on the Haas partner page (Nov 2026)',
 'MELI': 'Mercado Libre is on the Alpine partner page (Nov 2026)',
 'SSYS': 'Stratasys is on the McLaren partner page (Nov 2026)',
 'ABBV': 'AbbVie is on the McLaren partner page (Nov 2026)',
 'HINDUNILVR.NS': 'subsidiary of Unilever, whose Clear brand is a Red Bull Racing partner from 2026',
 'UNVR.JK': 'subsidiary of Unilever, whose Clear brand is a Red Bull Racing partner from 2026',
 'UPFL.PK': 'subsidiary of Unilever, whose Clear brand is a Red Bull Racing partner from 2026',
 'MBLY': 'majority-owned by Intel, a McLaren partner from 2026',
 '1128.HK': 'subsidiary of Wynn Resorts, a Las Vegas Grand Prix founding partner',
 '5838.T': 'subsidiary of Rakuten, a Ferrari partner from 2027',
}
