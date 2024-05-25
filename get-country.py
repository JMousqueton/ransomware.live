import json
import pycountry
import re
import tldextract
from sharedutils import stdlog

print(
    '''
       _______________                         |*\_/*|________
      |  ___________  |                       ||_/-\_|______  |
      | |           | |                       | |           | |
      | |   0   0   | |                       | |   0   0   | |
      | |     -     | |                       | |     -     | |
      | |   \___/   | |                       | |   \___/   | |
      | |___     ___| |                       | |___________| |
      |_____|\_/|_____|                       |_______________|
        _|__|/ \|_|_.............💔.............._|________|_
       / ********** \                           / ********** \ 
     /  ************  \  Ransomware.live      /  ************  \ 
    --------------------                     --------------------
    '''
)   
stdlog('Analyzing victims to get countries')

country_names = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", 
    "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", 
    "Belize", "Benin", "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", 
    "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", 
    "Chad", "Chile", "China", "Colombia", "Comoros", "Congo", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", 
    "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador", 
    "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France", 
    "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", 
    "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel", 
    "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, North", 
    "Korea, South", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", 
    "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", 
    "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", 
    "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", 
    "Nigeria", "North Macedonia", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", 
    "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", 
    "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", 
    "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", 
    "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Taiwan", 
    "Tajikistan", "Tanzania", "Thailand", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", 
    "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", 
    "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]

# Read the JSON file
with open('posts.json', 'r') as file:
    posts = json.load(file)

# Iterate through the posts
for post in posts:
    description = post.get('description', '')  # Get description or default to an empty string
    country = post['country']
    country_name =''

    # Check if description starts with "Country:" and country is empty
    if description.startswith("Country:") and not country:
        # Extract country name from the description
        country_name = description.replace("Country:", "").strip()
    if description.startswith("Country : ") and not country:
        country_name = description.split('-')[0].strip().replace("Country : ","")

    
    if not country and description and not country_name:
        for name_country in country_names:
            if name_country in description:
                 country_name = name_country

    if country_name:
        # Convert country name to two-letter country code
        try:
            country_code = pycountry.countries.lookup(country_name).alpha_2
            if country_code != 'EU':
                post['country'] = country_code
                stdlog('Methode 1 : ' + post['post_title'] + ' ---> ' +  country_code)
        except LookupError:
            #print(f"Country code not found for: {country_name}")
            pass

# Write the modified data back to the JSON file


# Mapping of TLDs to country codes
tld_country_mapping = {
    'com': '',  # Generic TLD (no specific country)
    'org': '',  # Generic TLD (no specific country)
    'net': '',  # Generic TLD (no specific country)
    'gov': '',  # Generic TLD (no specific country)
    'edu': '',  # Generic TLD (no specific country)
    'int': '',  # Generic TLD (no specific country)
    'mil': '',  # Generic TLD (no specific country)
    'biz': '',  # Generic TLD (no specific country)
    'info': '',  # Generic TLD (no specific country)
    'name': '',  # Generic TLD (no specific country)
    'eu': '',  # European Union

    # Country-specific TLDs
    'us': 'US',  # United States
    'uk': 'UK',  # United Kingdom
    'ca': 'CA',  # Canada
    'au': 'AU',  # Australia
    'de': 'DE',  # Germany
    'fr': 'FR',  # France
    'it': 'IT',  # Italy
    'es': 'ES',  # Spain
    'jp': 'JP',  # Japan
    'cn': 'CN',  # China
    'in': 'IN',  # India
    'ru': 'RU',  # Russia
    'br': 'BR',  # Brazil
    'mx': 'MX',  # Mexico
    'nl': 'NL',  # Netherlands
    'se': 'SE',  # Sweden
    'no': 'NO',  # Norway
    'fi': 'FI',  # Finland
    'dk': 'DK',  # Denmark
    'sg': 'SG',  # Singapore
    'za': 'ZA',  # South Africa
    'nz': 'NZ',  # New Zealand
    'ch': 'CH',  # Switzerland
    'at': 'AT',  # Austria
    'be': 'BE',  # Belgium
    'pt': 'PT',  # Portugal
    'pl': 'PL',  # Poland
    'ie': 'IE',  # Ireland
    'gr': 'GR',  # Greece
    'cz': 'CZ',  # Czech Republic
    'hu': 'HU',  # Hungary
    'ro': 'RO',  # Romania
    'tr': 'TR',  # Turkey
    'kr': 'KR',  # South Korea
    'il': 'IL',  # Israel
    'ae': 'AE',  # United Arab Emirates
    'sa': 'SA',  # Saudi Arabia
    'th': 'TH',  # Thailand
    'id': 'ID',  # Indonesia
    'my': 'MY',  # Malaysia
    'vn': 'VN',  # Vietnam
    'ph': 'PH',  # Philippines
    'cl': 'CL',  # Chile
    'co': 'CO',  # Colombia
    'ar': 'AR',  # Argentina
    'pe': 'PE',  # Peru
    've': 'VE',  # Venezuela
    'ng': 'NG',  # Nigeria
    'eg': 'EG',  # Egypt
    'za': 'ZA',  # South Africa
    'ke': 'KE',  # Kenya
    'ma': 'MA',  # Morocco
    'tn': 'TN',  # Tunisia
    'gh': 'GH',  # Ghana
    'dz': 'DZ',  # Algeria
    'ug': 'UG',  # Uganda
    'cm': 'CM',  # Cameroon
    'sn': 'SN',  # Senegal
    'zm': 'ZM',  # Zambia
    'bw': 'BW',  # Botswana
    'zw': 'ZW',  # Zimbabwe
    'mw': 'MW',  # Malawi
    'mu': 'MU',  # Mauritius
    'na': 'NA',  # Namibia
    'rw': 'RW',  # Rwanda
    'tz': 'TZ',  # Tanzania
    'et': 'ET',  # Ethiopia
    'ci': 'CI',  # Ivory Coast
    'gm': 'GM',  # Gambia
    'lr': 'LR',  # Liberia
    'mg': 'MG',  # Madagascar
    'mw': 'MW',  # Malawi
    'so': 'SO',  # Somalia
    'sd': 'SD',  # Sudan
    'tg': 'TG',  # Togo
    'ug': 'UG',  # Uganda
    'za': 'ZA',  # South Africa
    'ao': 'AO',  # Angola
    'cg': 'CG',  # Republic of the Congo
    'cd': 'CD',  # Democratic Republic of the Congo
    'gh': 'GH',  # Ghana
    'ke': 'KE',  # Kenya
    'mg': 'MG',  # Madagascar
    'mu': 'MU',  # Mauritius
    'mw': 'MW',  # Malawi
    'mz': 'MZ',  # Mozambique
    'na': 'NA',  # Namibia
    'rw': 'RW',  # Rwanda
    'sc': 'SC',  # Seychelles
    'sl': 'SL',  # Sierra Leone
    'ug': 'UG',  # Uganda
    'zm': 'ZM',  # Zambia
    'zw': 'ZW',  # Zimbabwe
    'rs': 'RS',  # Serbia
    'do': 'DO',  # Rep Dom.
}


# Regex pattern to validate domain names (FQDN)
domain_name_pattern = r"^([a-zA-Z0-9-]+(?:\.[a-zA-Z]+)+)$"

# Loop through each entry in the JSON
for entry in posts:
    website = entry.get('website')
    if entry['country'] == '' and website:
        website = website.replace('https://','').replace('http://','').replace('/','')
        if re.match(domain_name_pattern, website):
            domain_info = website.split('.')[-1] 
            if domain_info.lower() in tld_country_mapping:
                country_code = tld_country_mapping[domain_info.lower()]
                if country_code:
                    entry['country'] = country_code.upper() 
                    stdlog('Methode 2 : ' + entry['website'] + ' --> ' + str(entry['country']))

for entry in posts:
    if entry['country'] == '':
        post_title = entry['post_title']
        if re.match(domain_name_pattern, post_title):
            domain_info = post_title.split('.')[-1] 
        
            if domain_info.lower() in tld_country_mapping:
                country_code = tld_country_mapping[domain_info.lower()]
                if country_code:
                    entry['country'] = country_code.upper() 
                    stdlog('Methode 3 : ' + entry['post_title'] + ' --> ' + str(entry['country']))
        #else:
            #entry['country'] = None  # Not a valid FQDN                
            #print('Not a domain name --> ', post_title)



# Write the modified data back to the file
#with open('posts.json', 'w') as file:
#    json.dump(posts, file, indent=4)


with open('posts.json', 'w') as file:
    json.dump(posts, file, indent=4)

# Initialize counters
total_with_post_title = 0
total_with_post_title_2023  = 0
total_with_post_title_2024  = 0
with_country_and_post_title = 0
with_country_and_post_title_2023 = 0 
with_country_and_post_title_2024 = 0 

# Iterate over the posts
for entry in posts:
    if entry['discovered'].startswith("2023"):
           total_with_post_title_2023 +=1 
    if entry['discovered'].startswith("2024"):
            total_with_post_title_2024 +=1 
    total_with_post_title += 1
    if entry.get('country'):
        if entry['discovered'].startswith("2023"):
            with_country_and_post_title_2023 +=1 
        if entry['discovered'].startswith("2024"):
            with_country_and_post_title_2024 +=1 
        with_country_and_post_title += 1

# Calculate the percentage

percentage = (with_country_and_post_title / total_with_post_title) * 100
percentage_2023 = (with_country_and_post_title_2023 / total_with_post_title_2023) * 100
percentage_2024 = (with_country_and_post_title_2024 / total_with_post_title_2024) * 100
print(f"Percentage of victims entries with a country: {percentage:.2f}% based on {total_with_post_title} victims in the database")
print(f"Percentage of victims entries with a country in 2023 : {percentage_2023:.2f}% based on {total_with_post_title_2023} victims in the database")
print(f"Percentage of victims entries with a country in 2024 : {percentage_2024:.2f}% based on {total_with_post_title_2024} victims in the database")
