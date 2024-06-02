"""
Country Library

This module provides access to a comprehensive dataset of countries and territories,
each identified by their ISO 3166-1 alpha-2 country codes. It includes functionalities to:
- Retrieve the geographic coordinates (latitude and longitude) of a country using its ISO country code.
- Look up the ISO country code of a country based on its name.
- Get the official name of a country from its ISO country code.

The data is stored in a dictionary format, with each country code mapping to a tuple
that includes the country's name and its geographic coordinates.

Usage:
    from mypycountries import get_coordinates, get_country_code, get_country_name

    # Get coordinates from country code
    coords = get_coordinates('US')  # Returns (latitude, longitude)

    # Get country code from name
    country_code = get_country_code("United States of America")  # Returns 'US'

    # Get country name from country code
    country_name = get_country_name('US')  # Returns "United States of America"

    # Get Region from a country code 
    region_name = get_country_region('FR') # Returns "Europe"  

This library is useful for applications that require simple and direct access to geographic
data for countries without the need for external API calls or complex data management solutions.

Author: [Julien Mousqueton]
Version: 0.5
Last Updated: 2024-05-25
"""

country_coordinates = {
    'AF': ("Afghanistan", 33.93911, 67.709953, "South Asia"),
    'AX': ("Åland Islands", 60.1785247, 19.9156105, "Europe"),
    'AL': ("Albania", 41.153332, 20.168331, "Europe"),
    'DZ': ("Algeria", 28.033886, 1.659626, "Africa"),
    'AS': ("American Samoa", -14.270972, -170.132217, "Oceania"),
    'AD': ("Andorra", 42.546245, 1.601554, "Europe"),
    'AO': ("Angola", -11.202692, 17.873887, "Africa"),
    'AI': ("Anguilla", 18.220554, -63.068615, "North America"),
    'AQ': ("Antarctica", -75.250973, -0.071389, "Antarctica"),
    'AG': ("Antigua and Barbuda", 17.060816, -61.796428, "North America"),
    'AR': ("Argentina", -38.416097, -63.616672, "South America"),
    'AM': ("Armenia", 40.069099, 45.038189, "West Asia"),
    'AW': ("Aruba", 12.52111, -69.968338, "North America"),
    'AU': ("Australia", -25.274398, 133.775136, "Oceania"),
    'AT': ("Austria", 47.516231, 14.550072, "Europe"),
    'AZ': ("Azerbaijan", 40.143105, 47.576927, "West Asia"),
    'BS': ("Bahamas", 25.03428, -77.39628, "North America"),
    'BH': ("Bahrain", 25.930414, 50.637772, "West Asia"),
    'BD': ("Bangladesh", 23.684994, 90.356331, "South Asia"),
    'BB': ("Barbados", 13.193887, -59.543198, "North America"),
    'BY': ("Belarus", 53.709807, 27.953389, "Europe"),
    'BE': ("Belgium", 50.503887, 4.469936, "Europe"),
    'BZ': ("Belize", 17.189877, -88.49765, "North America"),
    'BJ': ("Benin", 9.30769, 2.315834, "Africa"),
    'BM': ("Bermuda", 32.321384, -64.75737, "North America"),
    'BT': ("Bhutan", 27.514162, 90.433601, "South Asia"),
    'BO': ("Bolivia", -16.290154, -63.588653, "South America"),
    'BA': ("Bosnia and Herzegovina", 43.915886, 17.679076, "Europe"),
    'BW': ("Botswana", -22.328474, 24.684866, "Africa"),
    'BV': ("Bouvet Island", -54.423199, 3.413194, "Antarctica"),
    'BR': ("Brazil", -14.235004, -51.92528, "South America"),
    'IO': ("British Indian Ocean Territory", -6.343194, 71.876519, "South Asia"),
    'BN': ("Brunei Darussalam", 4.535277, 114.727669, "Southeast Asia"),
    'BG': ("Bulgaria", 42.733883, 25.48583, "Europe"),
    'BF': ("Burkina Faso", 12.238333, -1.561593, "Africa"),
    'BI': ("Burundi", -3.373056, 29.918886, "Africa"),
    'CV': ("Cabo Verde", 16.002082, -24.013197, "Africa"),
    'KH': ("Cambodia", 12.565679, 104.990963, "Southeast Asia"),
    'CM': ("Cameroon", 7.369722, 12.354722, "Africa"),
    'CA': ("Canada", 56.130366, -106.346771, "North America"),
    'KY': ("Cayman Islands", 19.513469, -80.566956, "North America"),
    'CF': ("Central African Republic", 6.611111, 20.939444, "Africa"),
    'TD': ("Chad", 15.454166, 18.732207, "Africa"),
    'CL': ("Chile", -35.675147, -71.542969, "South America"),
    'CN': ("China", 35.86166, 104.195397, "East Asia"),
    'CX': ("Christmas Island", -10.447525, 105.690449, "Southeast Asia"),
    'CC': ("Cocos (Keeling) Islands", -12.164165, 96.870956, "Southeast Asia"),
    'CO': ("Colombia", 4.570868, -74.297333, "South America"),
    'KM': ("Comoros", -11.875001, 43.872219, "Africa"),
    'CD': ("Congo (Democratic Republic of the)", -4.038333, 21.758664, "Africa"),
    'CG': ("Congo", -0.228021, 15.827659, "Africa"),
    'CK': ("Cook Islands", -21.236736, -159.777671, "Oceania"),
    'CR': ("Costa Rica", 9.748917, -83.753428, "North America"),
    'HR': ("Croatia", 45.1, 15.2, "Europe"),
    'CU': ("Cuba", 21.521757, -77.781167, "North America"),
    'CW': ("Curaçao", 12.169570, -68.990020, "North America"),
    'CY': ("Cyprus", 35.126413, 33.429859, "West Asia"),
    'CZ': ("Czechia", 49.817492, 15.472962, "Europe"),
    'CI': ("Côte d'Ivoire", 7.539989, -5.54708, "Africa"),
    'DK': ("Denmark", 56.26392, 9.501785, "Europe"),
    'DJ': ("Djibouti", 11.825138, 42.590275, "Africa"),
    'DM': ("Dominica", 15.414999, -61.370976, "North America"),
    'DO': ("Dominican Republic", 18.735693, -70.162651, "North America"),
    'EC': ("Ecuador", -1.831239, -78.183406, "South America"),
    'EG': ("Egypt", 26.820553, 30.802498, "Africa"),
    'SV': ("El Salvador", 13.794185, -88.89653, "North America"),
    'GQ': ("Equatorial Guinea", 1.650801, 10.267895, "Africa"),
    'ER': ("Eritrea", 15.179384, 39.782334, "Africa"),
    'EE': ("Estonia", 58.595272, 25.013607, "Europe"),
    'SZ': ("Eswatini", -26.522503, 31.465866, "Africa"),
    'ET': ("Ethiopia", 9.145, 40.489673, "Africa"),
    'FK': ("Falkland Islands (Malvinas)", -51.796253, -59.523613, "South America"),
    'FO': ("Faroe Islands", 61.892635, -6.911806, "Europe"),
    'FJ': ("Fiji", -17.713371, 178.065032, "Oceania"),
    'FI': ("Finland", 61.92411, 25.748151, "Europe"),
    'FR': ("France", 46.227638, 2.213749, "Europe"),
    'GF': ("French Guiana", 3.933889, -53.125782, "South America"),
    'PF': ("French Polynesia", -17.679742, -149.406843, "Oceania"),
    'TF': ("French Southern Territories", -49.280366, 69.348557, "Antarctica"),
    'GA': ("Gabon", -0.803689, 11.609444, "Africa"),
    'GM': ("Gambia", 13.443182, -15.310139, "Africa"),
    'GE': ("Georgia", 42.315407, 43.356892, "West Asia"),
    'DE': ("Germany", 51.165691, 10.451526, "Europe"),
    'GH': ("Ghana", 7.946527, -1.023194, "Africa"),
    'GI': ("Gibraltar", 36.137741, -5.345374, "Europe"),
    'GR': ("Greece", 39.074208, 21.824312, "Europe"),
    'GL': ("Greenland", 71.706936, -42.604303, "North America"),
    'GD': ("Grenada", 12.262776, -61.604171, "North America"),
    'GP': ("Guadeloupe", 16.995971, -62.067641, "North America"),
    'GU': ("Guam", 13.444304, 144.793731, "Oceania"),
    'GT': ("Guatemala", 15.783471, -90.230759, "North America"),
    'GG': ("Guernsey", 49.465691, -2.585278, "Europe"),
    'GN': ("Guinea", 9.945587, -9.696645, "Africa"),
    'GW': ("Guinea-Bissau", 11.803749, -15.180413, "Africa"),
    'GY': ("Guyana", 4.860416, -58.93018, "South America"),
    'HT': ("Haiti", 18.971187, -72.285215, "North America"),
    'HM': ("Heard Island and McDonald Islands", -53.08181, 73.504158, "Antarctica"),
    'VA': ("Holy See", 41.902916, 12.453389, "Europe"),
    'HN': ("Honduras", 15.199999, -86.241905, "North America"),
    'HK': ("Hong Kong", 22.396428, 114.109497, "East Asia"),
    'HU': ("Hungary", 47.162494, 19.503304, "Europe"),
    'IS': ("Iceland", 64.963051, -19.020835, "Europe"),
    'IN': ("India", 20.593684, 78.96288, "South Asia"),
    'ID': ("Indonesia", -0.789275, 113.921327, "Southeast Asia"),
    'IR': ("Iran", 32.427908, 53.688046, "West Asia"),
    'IQ': ("Iraq", 33.223191, 43.679291, "West Asia"),
    'IE': ("Ireland", 53.41291, -8.24389, "Europe"),
    'IM': ("Isle of Man", 54.236107, -4.548056, "Europe"),
    'IL': ("Israel", 31.046051, 34.851612, "West Asia"),
    'IT': ("Italy", 41.87194, 12.56738, "Europe"),
    'JM': ("Jamaica", 18.109581, -77.297508, "North America"),
    'JP': ("Japan", 36.204824, 138.252924, "East Asia"),
    'JE': ("Jersey", 49.214439, -2.13125, "Europe"),
    'JO': ("Jordan", 30.585164, 36.238414, "West Asia"),
    'KZ': ("Kazakhstan", 48.019573, 66.923684, "Central Asia"),
    'KE': ("Kenya", -0.023559, 37.906193, "Africa"),
    'KI': ("Kiribati", -3.370417, -168.734039, "Oceania"),
    'KP': ("Korea (Democratic People's Republic of)", 40.339852, 127.510093, "East Asia"),
    'KR': ("Korea (Republic of)", 35.907757, 127.766922, "East Asia"),
    'KW': ("Kuwait", 29.31166, 47.481766, "West Asia"),
    'KG': ("Kyrgyzstan", 41.20438, 74.766098, "Central Asia"),
    'LA': ("Lao People's Democratic Republic", 19.85627, 102.495496, "Southeast Asia"),
    'LV': ("Latvia", 56.879635, 24.603189, "Europe"),
    'LB': ("Lebanon", 33.854721, 35.862285, "West Asia"),
    'LS': ("Lesotho", -29.609988, 28.233608, "Africa"),
    'LR': ("Liberia", 6.428055, -9.429499, "Africa"),
    'LY': ("Libya", 26.3351, 17.228331, "Africa"),
    'LI': ("Liechtenstein", 47.166, 9.555373, "Europe"),
    'LT': ("Lithuania", 55.169438, 23.881275, "Europe"),
    'LU': ("Luxembourg", 49.815273, 6.129583, "Europe"),
    'MO': ("Macao", 22.198745, 113.543873, "East Asia"),
    'MG': ("Madagascar", -18.766947, 46.869107, "Africa"),
    'MW': ("Malawi", -13.254308, 34.301525, "Africa"),
    'MY': ("Malaysia", 4.210484, 101.975766, "Southeast Asia"),
    'MV': ("Maldives", 3.202778, 73.22068, "South Asia"),
    'ML': ("Mali", 17.570692, -3.996166, "Africa"),
    'MT': ("Malta", 35.937496, 14.375416, "Europe"),
    'MH': ("Marshall Islands", 7.131474, 171.184478, "Oceania"),
    'MQ': ("Martinique", 14.641528, -61.024174, "North America"),
    'MR': ("Mauritania", 21.00789, -10.940835, "Africa"),
    'MU': ("Mauritius", -20.348404, 57.552152, "Africa"),
    'YT': ("Mayotte", -12.8275, 45.166244, "Africa"),
    'MX': ("Mexico", 23.634501, -102.552784, "North America"),
    'FM': ("Micronesia (Federated States of)", 7.425554, 150.550812, "Oceania"),
    'MD': ("Moldova (Republic of)", 47.411631, 28.369885, "Europe"),
    'MC': ("Monaco", 43.750298, 7.412841, "Europe"),
    'MN': ("Mongolia", 46.862496, 103.846656, "East Asia"),
    'ME': ("Montenegro", 42.708678, 19.37439, "Europe"),
    'MS': ("Montserrat", 16.742498, -62.187366, "North America"),
    'MA': ("Morocco", 31.791702, -7.09262, "Africa"),
    'MZ': ("Mozambique", -18.665695, 35.529562, "Africa"),
    'MM': ("Myanmar", 21.913965, 95.956223, "Southeast Asia"),
    'NA': ("Namibia", -22.95764, 18.49041, "Africa"),
    'NR': ("Nauru", -0.522778, 166.931503, "Oceania"),
    'NP': ("Nepal", 28.394857, 84.124008, "South Asia"),
    'NL': ("Netherlands", 52.132633, 5.291266, "Europe"),
    'NC': ("New Caledonia", -20.904305, 165.618042, "Oceania"),
    'NZ': ("New Zealand", -40.900557, 174.885971, "Oceania"),
    'NI': ("Nicaragua", 12.865416, -85.207229, "North America"),
    'NE': ("Niger", 17.607789, 8.081666, "Africa"),
    'NG': ("Nigeria", 9.081999, 8.675277, "Africa"),
    'NU': ("Niue", -19.054445, -169.867233, "Oceania"),
    'NF': ("Norfolk Island", -29.040835, 167.954712, "Oceania"),
    'MK': ("North Macedonia", 41.608635, 21.745275, "Europe"),
    'MP': ("Northern Mariana Islands", 17.33083, 145.38469, "Oceania"),
    'NO': ("Norway", 60.472024, 8.468946, "Europe"),
    'OM': ("Oman", 21.512583, 55.923255, "West Asia"),
    'PK': ("Pakistan", 30.375321, 69.345116, "South Asia"),
    'PW': ("Palau", 7.51498, 134.58252, "Oceania"),
    'PS': ("Palestine, State of", 31.952162, 35.233154, "West Asia"),
    'PA': ("Panama", 8.537981, -80.782127, "North America"),
    'PG': ("Papua New Guinea", -6.314993, 143.95555, "Oceania"),
    'PY': ("Paraguay", -23.442503, -58.443832, "South America"),
    'PE': ("Peru", -9.189967, -75.015152, "South America"),
    'PH': ("Philippines", 12.879721, 121.774017, "Southeast Asia"),
    'PN': ("Pitcairn", -24.703615, -127.439308, "Oceania"),
    'PL': ("Poland", 51.919438, 19.145136, "Europe"),
    'PT': ("Portugal", 39.399872, -8.224454, "Europe"),
    'PR': ("Puerto Rico", 18.220833, -66.590149, "North America"),
    'QA': ("Qatar", 25.354826, 51.183884, "West Asia"),
    'RE': ("Réunion", -21.115141, 55.536384, "Africa"),
    'RO': ("Romania", 45.943161, 24.96676, "Europe"),
    'RU': ("Russian Federation", 61.52401, 105.318756, "Europe"),
    'RW': ("Rwanda", -1.940278, 29.873888, "Africa"),
    'BL': ("Saint Barthélemy", 17.9, -62.833333, "North America"),
    'SH': ("Saint Helena, Ascension and Tristan da Cunha", -24.143474, -10.030696, "Africa"),
    'KN': ("Saint Kitts and Nevis", 17.357822, -62.782998, "North America"),
    'LC': ("Saint Lucia", 13.909444, -60.978893, "North America"),
    'MF': ("Saint Martin (French part)", 18.08255, -63.052251, "North America"),
    'PM': ("Saint Pierre and Miquelon", 46.941936, -56.27111, "North America"),
    'VC': ("Saint Vincent and the Grenadines", 12.984305, -61.287228, "North America"),
    'WS': ("Samoa", -13.759029, -172.104629, "Oceania"),
    'SM': ("San Marino", 43.94236, 12.457777, "Europe"),
    'ST': ("Sao Tome and Principe", 0.18636, 6.613081, "Africa"),
    'SA': ("Saudi Arabia", 23.885942, 45.079162, "West Asia"),
    'SN': ("Senegal", 14.497401, -14.452362, "Africa"),
    'RS': ("Serbia", 44.016521, 21.005859, "Europe"),
    'SC': ("Seychelles", -4.679574, 55.491977, "Africa"),
    'SL': ("Sierra Leone", 8.460555, -11.779889, "Africa"),
    'SG': ("Singapore", 1.352083, 103.819836, "Southeast Asia"),
    'SX': ("Sint Maarten (Dutch part)", 18.034718, -63.068111, "North America"),
    'SK': ("Slovakia", 48.669026, 19.699024, "Europe"),
    'SI': ("Slovenia", 46.151241, 14.995463, "Europe"),
    'SB': ("Solomon Islands", -9.64571, 160.156194, "Oceania"),
    'SO': ("Somalia", 5.152149, 46.199616, "Africa"),
    'ZA': ("South Africa", -30.559482, 22.937506, "Africa"),
    'GS': ("South Georgia and the South Sandwich Islands", -54.429579, -36.587909, "Antarctica"),
    'SS': ("South Sudan", 6.877, 31.307, "Africa"),
    'ES': ("Spain", 40.463667, -3.74922, "Europe"),
    'LK': ("Sri Lanka", 7.873054, 80.771797, "South Asia"),
    'SD': ("Sudan", 12.862807, 30.217636, "Africa"),
    'SR': ("Suriname", 3.919305, -56.027783, "South America"),
    'SJ': ("Svalbard and Jan Mayen", 77.553604, 23.670272, "Europe"),
    'SE': ("Sweden", 60.128161, 18.643501, "Europe"),
    'CH': ("Switzerland", 46.818188, 8.227512, "Europe"),
    'SY': ("Syrian Arab Republic", 34.802075, 38.996815, "West Asia"),
    'TW': ("Taiwan, Province of China", 23.69781, 120.960515, "East Asia"),
    'TJ': ("Tajikistan", 38.861034, 71.276093, "Central Asia"),
    'TZ': ("Tanzania, United Republic of", -6.369028, 34.888822, "Africa"),
    'TH': ("Thailand", 15.870032, 100.992541, "Southeast Asia"),
    'TL': ("Timor-Leste", -8.874217, 125.727539, "Southeast Asia"),
    'TG': ("Togo", 8.619543, 0.824782, "Africa"),
    'TK': ("Tokelau", -9.2002, -171.8484, "Oceania"),
    'TO': ("Tonga", -21.178986, -175.198242, "Oceania"),
    'TT': ("Trinidad and Tobago", 10.691803, -61.222503, "North America"),
    'TN': ("Tunisia", 33.886917, 9.537499, "Africa"),
    'TR': ("Turkey", 38.963745, 35.243322, "West Asia"),
    'TM': ("Turkmenistan", 38.969719, 59.556278, "Central Asia"),
    'TC': ("Turks and Caicos Islands", 21.694025, -71.797928, "North America"),
    'TV': ("Tuvalu", -7.109535, 177.64933, "Oceania"),
    'UG': ("Uganda", 1.373333, 32.290275, "Africa"),
    'UA': ("Ukraine", 48.379433, 31.16558, "Europe"),
    'AE': ("United Arab Emirates", 23.424076, 53.847818, "West Asia"),
    'GB': ("United Kingdom of Great Britain and Northern Ireland", 55.378051, -3.435973, "Europe"),
    'US': ("United States of America", 37.09024, -95.712891, "North America"),
    'UM': ("United States Minor Outlying Islands", 0, 0, "Oceania"),
    'UY': ("Uruguay", -32.522779, -55.765835, "South America"),
    'UZ': ("Uzbekistan", 41.377491, 64.585262, "Central Asia"),
    'VU': ("Vanuatu", -15.376706, 166.959158, "Oceania"),
    'VE': ("Venezuela (Bolivarian Republic of)", 6.42375, -66.58973, "South America"),
    'VN': ("Viet Nam", 14.058324, 108.277199, "Southeast Asia"),
    'VG': ("Virgin Islands (British)", 18.420695, -64.639968, "North America"),
    'VI': ("Virgin Islands (U.S.)", 18.335765, -64.896335, "North America"),
    'WF': ("Wallis and Futuna", -13.768752, -177.156097, "Oceania"),
    'EH': ("Western Sahara", 24.215527, -12.885834, "Africa"),
    'YE': ("Yemen", 15.552727, 48.516388, "West Asia"),
    'ZM': ("Zambia", -13.133897, 27.849332, "Africa"),
    'ZW': ("Zimbabwe", -19.015438, 29.154857, "Africa")
}

def get_coordinates(country_code):
    """Retrieve the coordinates of a country by its ISO two-letter code."""
    entry = country_coordinates.get(country_code.upper())
    if entry:
        return (entry[1], entry[2])
    return None

def get_country_code(country_name):
    """Retrieve the ISO two-letter country code by country name."""
    for code, details in country_coordinates.items():
        if details[0].lower() == country_name.lower():
            return code
    return None

def get_country_name(country_code):
    """Retrieve the country name by its ISO two-letter code."""
    entry = country_coordinates.get(country_code.upper())
    if entry:
        return entry[0]
    return None

def get_country_region(country_code):
    """Retrieve the region of a country by its ISO two-letter code."""
    entry = country_coordinates.get(country_code.upper())
    if entry:
        return entry[3]
    return None
