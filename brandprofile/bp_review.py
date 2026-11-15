"""Manual decisions for the brand workbook (keyed by brand id from data/brands.json.gz)."""
# id -> fields that replace the profile (after a web check)
FIX = {
 '48-0086': {'status': 'subsidiary', 'parent': 'ServiceNow', 'ticker': '', 'changed': 'Acquired by ServiceNow in April 2026', 'f1': ''},      # ServiceNow press release, 20 Apr 2026
 '08-0344': {'status': 'private', 'parent': '', 'ticker': '', 'f1': '', 'conf': 'medium',
             'changed': 'Bought by Meta in December 2025; China ordered the deal unwound in April 2026 and Manus was reported to be separating from Meta in August 2026'},
 '08-0349': {'status': 'private', 'parent': '', 'ticker': '', 'changed': 'Taken private by Hg in April 2026 and delisted from Nasdaq'},                # found by web search, 15 Nov 2026
 '08-0247': {'status': 'private', 'parent': '', 'ticker': '', 'changed': 'Taken private by Sycamore Partners in 2025 and split into separate Walgreens, Boots and other businesses; the holding company no longer exists'},
}
# id -> ('exclude' | 'note' | 'clear', text) for the Formula 1 link
F1 = {
 '26-0154': ('clear', ''),                                                   # Paramount Group is a New York office landlord, not Paramount+
 '13-1139': ('note', 'Owned by Carlyle, which is an F1 partner as an investment firm; Hexaware itself has no F1 deal'),
 '36-0034': ('note', 'Owned by Carlyle, which is an F1 partner as an investment firm; the company itself has no F1 deal'),
 '08-1280': ('note', 'Majority-owned by Carlyle, which is an F1 partner as an investment firm; Syniverse itself has no F1 deal'),
 '03-0083': ('note', 'Part of Carlyle Aviation Partners; Carlyle is an F1 partner as an investment firm'),
 '46-0211': ('note', 'Was bought by Goldman Sachs (an F1 partner) in 2019; Goldman later sold this business - confirm the current owner'),
 '18-0595': ('note', 'Sister company of Duracell (an F1 partner) inside Berkshire Hathaway; no F1 deal of its own'),
 '16-0576': ('note', 'Formerly owned by Berkshire Hathaway (owner of F1 partner Duracell); reported sold in 2019 - confirm'),
 '05-0005': ('note', 'Runs The Venetian Macao; The Venetian Resort Las Vegas (an F1 partner) is under separate ownership'),
 '09-0001': ('note', 'Streams "Formula 1: Drive to Survive": a content relationship with F1, not a sponsorship'),
 '09-0004': ('note', 'Holds the US broadcast rights to Formula 1 from 2026 (Apple TV): a media-rights partner of F1, not a sponsor'),
 '11-0321': ('note', 'Owned by Apple, which holds the US broadcast rights to Formula 1 from 2026: a media-rights partner, not a sponsor'),
 '09-0053': ('note', 'Holds the French broadcast rights to Formula 1: a media-rights partner, not a sponsor'),
 '02-0039': ('note', 'Abu Dhabi state holding company reported to own Etihad Airways (an F1 partner); ADQ itself is not a partner'),
 '19-0199': ('note', 'Owned by Mumtalakat, the Bahrain state fund that also owns Gulf Air (an F1 partner); no F1 deal of its own'),
 '46-0215': ('clear', ''),                                                   # Boeing sold Jeppesen ForeFlight to Thoma Bravo (closed Nov 2025; web spot-check)
 '06-0119': ('note', 'Was part of Topgolf Callaway Brands (owner of F1 partner TravisMathew); a majority sale was reported in 2025-26 - confirm'),
 '27-0037': ('note', 'Was the Indian arm of AkzoNobel (Sikkens is an F1 partner); a sale to JSW Paints was reported in 2025 - confirm'),
 '23-0038': ('note', 'Sells Gulf-branded fuel in the United States under licence; Gulf Oil International (an F1 partner) is a separate company'),
 '08-0192': ('note', 'Name refers to Anthropic (an F1 partner); ownership not confirmed'),
 # after the second check (web-confirmed 15 Nov 2026)
 '08-0303': ('exclude', "IndraMind, Indra Group's AI brand, is a BWT Alpine F1 Team partner (announced January 2026)"),
 '48-0086': ('exclude', 'ServiceNow (Formula 1 partner) completed its acquisition of Armis in April 2026'),
 '01-0268': ('exclude', 'Parent of Iveco (an F1 partner): Tata Motors completed its takeover of Iveco Group in October 2026'),
 '08-0344': ('note', 'Meta (an F1 partner) bought Manus in December 2025; China ordered the deal unwound and Manus was reported to be separating from Meta in 2026 - confirm the current owner'),
 '09-0014': ('note', 'Owns Sky, which holds F1 broadcast rights in the UK, Italy and Germany: a media-rights partner of F1, not a sponsor'),
 '07-0013': ('note', "Runs Formula 1's official online store under a merchandise licence: a licensing partner of F1, not a sponsor"),
}
# id -> listed-company symbol, where the automatic match needs help
SYM = {}
# Blind web spot-check (data/spot_web.jsonl): rows left as they were, with the reason
SPOT_SKIP = {'15-0003', '15-0087', '36-1644'}     # the web result may describe a different group entity (Brookfield, Mirae Asset, HEC)
SPOT_KEEP_HQ = {'01-0143'}                        # Garmin: Swiss legal domicile, operating headquarters in Olathe
SPOT_KEEP_REACH = {'18-0741'}                     # Shoals: international revenue is marginal, so Domestic stands
# lines for the Research Summary
ACCURACY = []
LIMITS = []
