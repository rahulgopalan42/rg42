"""HQ country from Crunchbase "City, Region, Country" strings, which the results table often truncates
("Austin, Texas, United St...", "Stellenbosch, NA - South ..."). The country is read from the last part when it is
complete or a unique prefix; otherwise from the region (US states, Chinese provinces, ...) or a known city."""
import re, difflib

COUNTRIES = ['United States', 'United Kingdom', 'United Arab Emirates', 'China', 'India', 'Germany', 'France', 'Canada', 'Japan', 'South Korea',
             'Israel', 'Singapore', 'Australia', 'Brazil', 'Spain', 'Italy', 'Netherlands', 'Sweden', 'Switzerland', 'Hong Kong', 'Taiwan',
             'Indonesia', 'Mexico', 'Ireland', 'Norway', 'Denmark', 'Finland', 'Belgium', 'Austria', 'Poland', 'Portugal', 'Luxembourg',
             'Saudi Arabia', 'Qatar', 'Kuwait', 'Bahrain', 'Oman', 'Egypt', 'Nigeria', 'Kenya', 'South Africa', 'Morocco', 'Ghana', 'Turkey',
             'Russia', 'Ukraine', 'Estonia', 'Lithuania', 'Latvia', 'Czech Republic', 'Slovakia', 'Hungary', 'Romania', 'Bulgaria', 'Greece',
             'Cyprus', 'Malta', 'Croatia', 'Serbia', 'Slovenia', 'Iceland', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Uruguay', 'Ecuador',
             'Venezuela', 'Costa Rica', 'Panama', 'Guatemala', 'Dominican Republic', 'Puerto Rico', 'Jamaica', 'Bermuda', 'Cayman Islands',
             'British Virgin Islands', 'Bahamas', 'Barbados', 'Vietnam', 'Thailand', 'Malaysia', 'Philippines', 'Pakistan', 'Bangladesh',
             'Sri Lanka', 'Nepal', 'Kazakhstan', 'Uzbekistan', 'Georgia', 'Armenia', 'Azerbaijan', 'Mongolia', 'New Zealand', 'Jordan',
             'Lebanon', 'Iraq', 'Iran', 'Tunisia', 'Algeria', 'Ethiopia', 'Tanzania', 'Uganda', 'Rwanda', 'Senegal', "Côte d'Ivoire",
             'Ivory Coast', 'Cameroon', 'Zimbabwe', 'Zambia', 'Mozambique', 'Angola', 'Botswana', 'Namibia', 'Mauritius', 'Macau', 'Monaco',
             'Liechtenstein', 'Jersey', 'Guernsey', 'Isle of Man', 'Gibraltar', 'Belarus', 'Moldova', 'Bosnia and Herzegovina', 'North Macedonia',
             'Albania', 'Montenegro', 'Cambodia', 'Myanmar', 'Laos', 'Brunei', 'Papua New Guinea', 'Fiji', 'Trinidad and Tobago', 'Bolivia',
             'Paraguay', 'Honduras', 'El Salvador', 'Nicaragua', 'Kyrgyzstan', 'Tajikistan', 'Turkmenistan', 'Afghanistan', 'Syria', 'Yemen',
             'Libya', 'Sudan', 'Mali', 'Burkina Faso', 'Niger', 'Madagascar', 'Malawi', 'Republic of Korea', 'Korea, Republic of']
ALIAS = {'Republic of Korea': 'South Korea', 'Korea, Republic of': 'South Korea', 'Ivory Coast': "Côte d'Ivoire", 'The Netherlands': 'Netherlands',
         'Czechia': 'Czech Republic', 'Türkiye': 'Turkey', 'Russian Federation': 'Russia', 'Viet Nam': 'Vietnam', 'UAE': 'United Arab Emirates'}

US = 'Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia Hawaii Idaho Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada New_Hampshire New_Jersey New_Mexico New_York North_Carolina North_Dakota Ohio Oklahoma Oregon Pennsylvania Rhode_Island South_Carolina South_Dakota Tennessee Texas Utah Vermont Virginia Washington West_Virginia Wisconsin Wyoming District_of_Columbia'
REGIONS = {
    'United States': [x.replace('_', ' ') for x in US.split()],
    'Canada': ['Ontario', 'Quebec', 'British Columbia', 'Alberta', 'Manitoba', 'Saskatchewan', 'Nova Scotia', 'New Brunswick', 'Newfoundland', 'Prince Edward Island', 'Yukon'],
    'United Kingdom': ['England', 'Scotland', 'Wales', 'Northern Ireland', 'Greater London', 'Greater Manchester', 'West Midlands', 'Hertfordshire',
                       'Surrey', 'Berkshire', 'Oxfordshire', 'Cambridgeshire', 'Kent', 'Essex', 'Hampshire', 'Buckinghamshire', 'West Yorkshire',
                       'South Yorkshire', 'Merseyside', 'Lancashire', 'Bristol', 'Gloucestershire', 'Wiltshire', 'Somerset', 'Devon', 'Cornwall',
                       'Leicestershire', 'Nottinghamshire', 'Derbyshire', 'Warwickshire', 'Northamptonshire', 'Bedfordshire', 'Sussex', 'West Sussex',
                       'East Sussex', 'Norfolk', 'Suffolk', 'Cheshire', 'Tyne and Wear', 'Edinburgh', 'Glasgow City', 'Aberdeen City', 'Cardiff'],
    'China': ['Beijing', 'Shanghai', 'Guangdong', 'Zhejiang', 'Jiangsu', 'Shandong', 'Sichuan', 'Hubei', 'Hunan', 'Fujian', 'Anhui', 'Henan', 'Hebei',
              'Shaanxi', 'Shanxi', 'Liaoning', 'Jilin', 'Heilongjiang', 'Jiangxi', 'Guangxi', 'Yunnan', 'Guizhou', 'Chongqing', 'Tianjin', 'Hainan',
              'Gansu', 'Qinghai', 'Ningxia', 'Xinjiang', 'Tibet', 'Inner Mongolia', 'Nei Mongol'],
    'India': ['Maharashtra', 'Karnataka', 'Haryana', 'Delhi', 'Tamil Nadu', 'Telangana', 'Uttar Pradesh', 'Gujarat', 'West Bengal', 'Rajasthan',
              'Kerala', 'Andhra Pradesh', 'Madhya Pradesh', 'Punjab', 'Goa', 'Odisha', 'Bihar', 'Chandigarh'],
    'Australia': ['New South Wales', 'Victoria', 'Queensland', 'Western Australia', 'South Australia', 'Tasmania', 'Australian Capital Territory', 'Northern Territory'],
    'Germany': ['Bayern', 'Bavaria', 'Berlin', 'Hamburg', 'Hessen', 'Hesse', 'Nordrhein-Westfalen', 'North Rhine-Westphalia', 'Baden-Wurttemberg', 'Baden-Württemberg',
                'Niedersachsen', 'Lower Saxony', 'Sachsen', 'Saxony', 'Rheinland-Pfalz', 'Schleswig-Holstein', 'Brandenburg', 'Thuringen', 'Bremen', 'Saarland'],
    'France': ['Ile-de-France', 'Île-de-France', "Provence-Alpes-Cote d'Azur", 'Auvergne-Rhone-Alpes', 'Rhone-Alpes', 'Midi-Pyrenees', 'Occitanie', 'Nouvelle-Aquitaine',
               'Aquitaine', 'Hauts-de-France', 'Nord-Pas-de-Calais', 'Bretagne', 'Pays de la Loire', 'Grand Est', 'Alsace', 'Normandie', 'Languedoc-Roussillon'],
    'Brazil': ['Sao Paulo', 'São Paulo', 'Rio de Janeiro', 'Minas Gerais', 'Parana', 'Paraná', 'Santa Catarina', 'Rio Grande do Sul', 'Bahia', 'Pernambuco', 'Distrito Federal'],
    'Japan': ['Tokyo', 'Osaka', 'Kanagawa', 'Aichi', 'Kyoto', 'Hyogo', 'Fukuoka', 'Hokkaido', 'Saitama', 'Chiba', 'Shizuoka', 'Hiroshima'],
    'South Korea': ['Seoul', "Seoul-t'ukpyolsi", 'Gyeonggi-do', 'Kyonggi-do', 'Busan', 'Incheon', 'Daejeon', 'Gyeonggi'],
    'Spain': ['Madrid', 'Catalonia', 'Cataluna', 'Cataluña', 'Andalucia', 'Valencia', 'Comunidad Valenciana', 'Pais Vasco', 'Basque Country', 'Galicia', 'Navarra'],
    'Italy': ['Lombardia', 'Lombardy', 'Lazio', 'Piemonte', 'Veneto', 'Emilia-Romagna', 'Toscana', 'Tuscany', 'Campania', 'Liguria', 'Sicilia', 'Puglia'],
    'Switzerland': ['Zurich', 'Zürich', 'Geneve', 'Genève', 'Geneva', 'Vaud', 'Basel-Stadt', 'Bern', 'Zug', 'Luzern', 'Ticino', 'Schwyz', 'Aargau', 'Basel-Landschaft'],
    'Netherlands': ['Noord-Holland', 'North Holland', 'Zuid-Holland', 'South Holland', 'Utrecht', 'Noord-Brabant', 'North Brabant', 'Gelderland', 'Overijssel', 'Groningen', 'Limburg'],
    'Sweden': ['Stockholms Lan', 'Stockholms Län', 'Vastra Gotalands Lan', 'Västra Götalands Län', 'Skane Lan', 'Skåne Län', 'Uppsala Lan'],
    'Israel': ['Tel Aviv', 'HaMerkaz', 'Central District', 'Haifa', 'Jerusalem', 'HaZafon', 'HaDarom'],
    'United Arab Emirates': ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras al-Khaimah'],
    'Mexico': ['Distrito Federal', 'Ciudad de Mexico', 'Nuevo Leon', 'Nuevo León', 'Jalisco', 'Coahuila', 'Estado de Mexico'],
    'Indonesia': ['Jakarta Raya', 'DKI Jakarta', 'Jawa Barat', 'Jawa Timur', 'Banten', 'Bali'],
    'Singapore': ['Central Region'],
    'Ireland': ['Dublin', 'Cork', 'Galway'],
    'Hong Kong': ['Hong Kong Island', 'Kowloon', 'New Territories'],
    'Taiwan': ["T'ai-pei", 'Taipei', 'Hsinchu', 'Taichung', 'Kaohsiung', 'Tainan'],
    'Saudi Arabia': ['Ar Riyad', 'Riyadh', 'Makkah', 'Ash Sharqiyah', 'Eastern Province'],
    'South Africa': ['Gauteng', 'Western Cape', 'KwaZulu-Natal', 'Eastern Cape'],
    'Nigeria': ['Lagos', 'Abuja Federal Capital Territory', 'Federal Capital Territory'],
    'Argentina': ['Buenos Aires', 'Distrito Federal', 'Cordoba', 'Santa Fe'],
    'Chile': ['Region Metropolitana', 'Región Metropolitana', 'Santiago Metropolitan'],
    'Colombia': ['Distrito Especial', 'Antioquia', 'Cundinamarca', 'Bogota D.C.'],
    'Turkey': ['Istanbul', 'Ankara', 'Izmir'],
    'Norway': ['Oslo', 'Akershus', 'Rogaland', 'Hordaland', 'Viken', 'Vestland', 'More og Romsdal', 'Møre og Romsdal', 'Trondelag', 'Trøndelag', 'Agder', 'Vestfold', 'Nordland'],
    'Denmark': ['Hovedstaden', 'Midtjylland', 'Syddanmark', 'Sjaelland', 'Nordjylland'],
    'Finland': ['Uusimaa', 'Southern Finland', 'Pirkanmaa'],
    'Austria': ['Wien', 'Vienna', 'Oberosterreich', 'Steiermark', 'Tirol', 'Salzburg', 'Niederosterreich'],
    'Belgium': ['Brussels Hoofdstedelijk Gewest', 'Brussels', 'Vlaams-Brabant', 'Antwerpen', 'Oost-Vlaanderen', 'Brabant Wallon', 'Liege'],
    'Poland': ['Mazowieckie', 'Malopolskie', 'Dolnoslaskie', 'Wielkopolskie', 'Pomorskie'],
    'Vietnam': ['Ho Chi Minh', 'Ha Noi', 'Hanoi'],
    'Thailand': ['Krung Thep', 'Bangkok'],
    'Malaysia': ['Kuala Lumpur', 'Selangor', 'Penang', 'Pulau Pinang', 'Johor'],
    'Philippines': ['National Capital Region', 'Metro Manila', 'Makati'],
    'Kenya': ['Nairobi Area', 'Nairobi'],
    'Egypt': ['Al Qahirah', 'Cairo'],
    'Russia': ["Moscow City", "Moskva", "Saint Petersburg City"],
    'Portugal': ['Lisboa', 'Lisbon', 'Porto'],
    'Luxembourg': ['Luxembourg'],
    'Pakistan': ['Sindh', 'Islamabad', 'Khyber Pakhtunkhwa'],

}
CITIES = {'Stellenbosch': 'South Africa', 'Johannesburg': 'South Africa', 'Cape Town': 'South Africa', 'London': 'United Kingdom', 'Singapore': 'Singapore',
          'Hong Kong': 'Hong Kong', 'Dubai': 'United Arab Emirates', 'Abu Dhabi': 'United Arab Emirates', 'Riyadh': 'Saudi Arabia', 'Doha': 'Qatar',
          'Seoul': 'South Korea', 'Tokyo': 'Japan', 'Paris': 'France', 'Berlin': 'Germany', 'Munich': 'Germany', 'Amsterdam': 'Netherlands',
          'Stockholm': 'Sweden', 'Zurich': 'Switzerland', 'Geneva': 'Switzerland', 'Tel Aviv': 'Israel', 'Bangalore': 'India', 'Bengaluru': 'India',
          'Mumbai': 'India', 'Gurgaon': 'India', 'Gurugram': 'India', 'New Delhi': 'India', 'Sydney': 'Australia', 'Melbourne': 'Australia',
          'Toronto': 'Canada', 'Vancouver': None, 'Sao Paulo': 'Brazil', 'São Paulo': 'Brazil', 'Mexico City': 'Mexico', 'Jakarta': 'Indonesia',
          'Lagos': 'Nigeria', 'Nairobi': 'Kenya', 'Cairo': 'Egypt', 'Istanbul': 'Turkey', 'Madrid': 'Spain', 'Barcelona': 'Spain', 'Milan': 'Italy',
          'Dublin': 'Ireland', 'Oslo': 'Norway', 'Copenhagen': 'Denmark', 'Helsinki': 'Finland', 'Vienna': 'Austria', 'Brussels': 'Belgium',
          'Warsaw': 'Poland', 'Lisbon': 'Portugal', 'Taipei': 'Taiwan', 'Kuala Lumpur': 'Malaysia', 'Bangkok': 'Thailand', 'Manila': 'Philippines',
          'Ho Chi Minh City': 'Vietnam', 'Hanoi': 'Vietnam', 'Beijing': 'China', 'Shanghai': 'China', 'Shenzhen': 'China', 'Hangzhou': 'China',
          'Guangzhou': 'China', 'Buenos Aires': 'Argentina', 'Santiago': 'Chile', 'Bogota': 'Colombia', 'Bogotá': 'Colombia', 'Lima': 'Peru',
          'Montevideo': 'Uruguay', 'Luxembourg': 'Luxembourg', 'Monaco': 'Monaco', 'Tallinn': 'Estonia', 'Vilnius': 'Lithuania', 'Riga': 'Latvia',
          'Prague': 'Czech Republic', 'Budapest': 'Hungary', 'Bucharest': 'Romania', 'Sofia': 'Bulgaria', 'Athens': 'Greece', 'Kyiv': 'Ukraine',
          'Moscow': 'Russia', 'Almaty': 'Kazakhstan', 'Karachi': 'Pakistan', 'Lahore': 'Pakistan', 'Dhaka': 'Bangladesh', 'Colombo': 'Sri Lanka',
          'Auckland': 'New Zealand', 'Wellington': 'New Zealand', 'Amman': 'Jordan', 'Beirut': 'Lebanon', 'Manama': 'Bahrain', 'Muscat': 'Oman',
          'Kuwait City': 'Kuwait', 'Casablanca': 'Morocco', 'Accra': 'Ghana', 'Kigali': 'Rwanda', 'Addis Ababa': 'Ethiopia', 'Harare': 'Zimbabwe'}
_REG = {}
for c, rs in REGIONS.items():
    for r in rs: _REG.setdefault(r.lower(), set()).add(c)
_CTRY = {c.lower(): ALIAS.get(c, c) for c in COUNTRIES}

def _clean(p): return re.sub(r'[.…·]+$', '', p).strip(' .,-')

def _prefix_country(p, region=''):
    """'United St' -> United States; 'Unit' -> ambiguous unless the region decides"""
    pl = p.lower()
    if not pl: return None
    if pl in _CTRY: return _CTRY[pl]
    cands = [v for k, v in _CTRY.items() if k.startswith(pl)]
    if len(set(cands)) == 1: return cands[0]
    if cands and region:
        rc = _REG.get(region.lower(), set())
        both = [c for c in cands if c in rc]
        if len(set(both)) == 1: return both[0]
    return None

def country_of(hq):
    hq = re.sub(r'\s+', ' ', str(hq or '')).strip()
    if not hq: return ''
    parts = [p.strip() for p in re.split(r',', hq)]
    trunc = bool(re.search(r'(\.\.|…)\s*$', hq))
    last = _clean(parts[-1])
    last = re.sub(r'^(NA|N/A)\s*-\s*', '', last)            # "Stellenbosch, NA - South Africa"
    region = _clean(parts[1]) if len(parts) >= 3 else (_clean(parts[1]) if len(parts) == 2 and trunc else '')
    region = re.sub(r'^(NA|N/A)\s*-\s*', '', region)
    city = _clean(parts[0])
    if region.lower() in _CTRY and (len(parts) >= 3 and trunc): return _CTRY[region.lower()]
    if len(parts) >= 2:
        if not trunc or len(parts) >= 3:
            c = _prefix_country(last, region) if trunc else _CTRY.get(last.lower())
            if c: return c
            if not trunc:                                     # OCR typo in a complete country name
                m = difflib.get_close_matches(last.lower(), list(_CTRY), 1, 0.8)
                if m: return _CTRY[m[0]]
    # region decides (US state, Chinese province ...)
    for r in ([region] if region else []) + ([_clean(parts[1])] if len(parts) >= 2 else []):
        rc = _REG.get(r.lower())
        if rc and len(rc) == 1: return next(iter(rc))
        if r:
            m = difflib.get_close_matches(r.lower(), list(_REG), 1, 0.85)
            if m and len(_REG[m[0]]) == 1: return next(iter(_REG[m[0]]))
    if len(parts) >= 2 and trunc:
        c = _prefix_country(last, region)
        if c: return c
        r = _clean(parts[-1]).lower()                         # "Welwyn Garden City, Hertfor..." : region cut short
        if len(r) >= 4:
            cs = {c for k, v in _REG.items() if k.startswith(r) for c in v}
            if len(cs) == 1: return next(iter(cs))
    if CITIES.get(city): return CITIES[city]
    c = _CTRY.get(city.lower())
    return c or ''

if __name__ == '__main__':
    for s in ['Austin, Texas, United St...', 'Stellenbosch, NA - South ...', 'Independence, Ohio, Unit...', 'Shanghai, Shanghai, China',
              'London, England, United ...', 'St. Helier, NA - Jersey, Ch...', 'Rodez, Midi-Pyrenees, Fr...', "Taipei, T'ai-pei, Taiwan",
              'Sao Paulo, Sao Paulo, Bra...', 'Dubai, Dubai, United Arab ...', 'Calgary, Alberta, Canada', 'Gurugram, Haryana, India',
              'Paris, Ile-de-France, Fran...', 'Tel Aviv, Tel Aviv, Israel', 'Madrid, Madrid, Spain', 'Epalinges, Vaud, Switzerl...',
              'Westminster, Colorado, Un..', 'Wuhan, Hubei, China', 'Seoul, Seoul-t\'ukpyolsi, ...', 'Singapore, Central Region, ...']:
        print(f'{s!r:40} -> {country_of(s)}')
