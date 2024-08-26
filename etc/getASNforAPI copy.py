import re
import geoip2.database
from collections import Counter

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
    
    provider_counter = Counter()
    country_counter = Counter()

    for ip in ip_addresses:
        try:
            asn_response = asn_reader.asn(ip)
            provider = asn_response.autonomous_system_organization
            provider_counter[provider] += 1
            
            country_response = country_reader.country(ip)
            country = country_response.country.name
            country_counter[country] += 1
            
        except geoip2.errors.AddressNotFoundError:
            provider_counter['Unknown'] += 1
            country_counter['Unknown'] += 1

    asn_reader.close()
    country_reader.close()
    
    return provider_counter, country_counter

# Define file paths
log_file_path = '/var/log/nginx/api.access.log'
asn_database_path = '/var/www/ransomware-ng/import/GeoLite2-ASN.mmdb'
country_database_path = '/var/www/ransomware-ng/import/GeoLite2-Country.mmdb'

# Step 3: Set the minimum occurrences threshold
min_occurrences = 100
    
# Step 4: Execute the functions
ip_addresses = extract_ip_addresses(log_file_path)
provider_counter, country_counter = query_asn_and_country_database(ip_addresses, asn_database_path, country_database_path)

# Step 5: Sort providers and countries by occurrence, apply threshold, and print
sorted_providers = [(provider, count) for provider, count in provider_counter.most_common() if count >= min_occurrences]
sorted_countries = [(country, count) for country, count in country_counter.most_common() if count >= min_occurrences]

print("Unique Providers Ordered by Occurrence (with at least {} occurrences):".format(min_occurrences))
for provider, count in sorted_providers:
    print(f"Provider: {provider}, Occurrences: {count}")

print("\nUnique Countries Ordered by Occurrence (with at least {} occurrences):".format(min_occurrences))
for country, count in sorted_countries:
    print(f"Country: {country}, Occurrences: {count}")
