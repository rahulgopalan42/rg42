"""Manual decisions for the brand workbook (keyed by brand id from data/brands.json.gz)."""
# id -> fields that replace the profile (after a web check)
FIX = {}
# id -> ('exclude' | 'note' | 'clear', text) for the Formula 1 link
F1 = {}
# id -> listed-company symbol, where the automatic match needs help
SYM = {}
# lines for the Research Summary
ACCURACY = []
LIMITS = []
