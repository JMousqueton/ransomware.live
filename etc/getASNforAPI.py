import re
import geoip2.database
from collections import defaultdict

# Step 1: Extract IP addresses from the Nginx log file
def extract_ip_addresses(log_file_path):
    ip_pattern = re.compile(r'^\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    ip_addresses = []

    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            match = re.match(ip_pattern, line)
            if match:
                ip_addresses.append(match.group())
    
    return ip_addresses

# Step 2: Query the GeoLite2 ASN and Country databases and count providers and countries
def query_asn_and_country_database(ip_addresses, asn_database_path, country_database_path):
    asn_reader = geoip2.database.Reader(asn_database_path)
    country_reader = geoip2.database.Reader(country_database_path)
    
    asn_country_info = defaultdict(lambda: {'ASN': None, 'Organization': None, 'Country': None, 'Count': 0, 'IPs': set()})

    for ip in ip_addresses:
        try:
            # Query ASN database
            asn_response = asn_reader.asn(ip)
            asn = asn_response.autonomous_system_number
            provider = asn_response.autonomous_system_organization
            
            # Query Country database
            country_response = country_reader.country(ip)
            country = country_response.country.name
            
            # Update the dictionary
            key = (asn, provider)
            asn_country_info[key]['ASN'] = asn
            asn_country_info[key]['Organization'] = provider
            asn_country_info[key]['Country'] = country
            asn_country_info[key]['Count'] += 1
            asn_country_info[key]['IPs'].add(ip)  # Add the IP to the set
            
        except geoip2.errors.AddressNotFoundError:
            pass  # Handle the case where the IP is not found in the database

    asn_reader.close()
    country_reader.close()
    
    return asn_country_info

# Define file paths
log_file_path = '/var/log/nginx/api.access.log'
asn_database_path = '/var/www/ransomware-ng/import/GeoLite2-ASN.mmdb'
country_database_path = '/var/www/ransomware-ng/import/GeoLite2-Country.mmdb'

# Step 3: Set the minimum occurrences threshold
min_occurrences = 5

# Step 4: Execute the functions
ip_addresses = extract_ip_addresses(log_file_path)
asn_country_info = query_asn_and_country_database(ip_addresses, asn_database_path, country_database_path)

# Step 5: Filter and print the results
print("Unique ASNs and their Associated Countries Ordered by Occurrence (with at least {} occurrences):".format(min_occurrences))
for (asn, provider), info in sorted(asn_country_info.items(), key=lambda item: item[1]['Count'], reverse=True):
    if info['Count'] >= min_occurrences:
        ips = ', '.join(info['IPs'])  # Join all IPs into a single string
        print(f"ASN: {asn}, Provider: {provider}, Country: {info['Country']}, Occurrences: {info['Count']} (IPs: {ips})")
