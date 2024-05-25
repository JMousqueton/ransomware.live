# Function to check if reverse DNS contains unwanted domains
filter_reverse_dns() {
    if [[ "$1" == *"linodeusercontent.com"* || "$1" == *"amazonaws.com"* ]]; then
        return 0  # Return 0 if the reverse DNS contains unwanted domains
    else
        return 1  # Return 1 otherwise
    fi
}

# Function to display help
display_help() {
    echo "Usage: log.sh [OPTIONS]"
    echo "Options:"
    echo "  -l, --log-type TYPE     Set the log type (api, ransomware, data)"
    echo "  -c, --clean             Clean option to filter unwanted domains"
    echo "  -r, --rss                   Only rss feed (only with -l ransomware)"
    echo "  -h, --help              Display this help message"
    exit 0
}

# Function to fetch netname from whois
get_netname() {
    netname=$(whois "$1" | grep -i "netname:" | awk -F ':' '{print $2}' | tr -d '[:space:]')
    echo "$netname"
}

# Function to fetch country from IP
get_country() {
    #country=$(curl -s "https://ipinfo.io/$1/country")
    country=$(whois "$1" | grep -m 1 -i "country:" | awk -F ':' '{print $2}' | tr -d '[:space:]')
    echo "$country"
}

# Set default log type and RSS option
log_type="ransomware"
rss_option=false
clean_option=false

# Validate and handle command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -l|--log-type)
            shift
            log_type=$1
            if [[ ! $log_type =~ ^(api|ransomware|data)$ ]]; then
                echo "Invalid argument for -l. Use 'api', 'ransomware', or 'data'."
                exit 1
            fi
            ;;
        -c|--clean)
            clean_option=true
            ;;
        -r|--rss)
            if [[ $log_type != "ransomware" ]]; then
                echo "--rss option only works with -l ransomware."
                exit 1
            fi
            rss_option=true
            ;;
        -h|--help)
            display_help
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

# Function to process IPs based on options
process_ips() {
    while read -r count ip; do
        reverse_dns=$(host "$ip" | awk '/pointer/ {print $5}' | head -n 1)

        if $clean_option; then
            if ! filter_reverse_dns "$reverse_dns"; then
                netname=$(get_netname "$ip")
                country=$(get_country "$ip")
                echo "IP: $ip - Occurrences: $count - Reverse DNS: ${reverse_dns:-Not available} - Netname: ${netname:-Not available} - Country: ${country:-Not available}"
            fi
        else
            netname=$(get_netname "$ip")
            country=$(get_country "$ip")
            echo "IP: $ip - Occurrences: $count - Reverse DNS: ${reverse_dns:-Not available} - Netname: ${netname:-Not available} - Country: ${country:-Not available}"
        fi
    done <<< "$sorted_ips"
}

# Determine log file based on log type
case $log_type in
    api)
        log_file="/var/log/nginx/api.access.log"
        ;;
    ransomware)
        log_file="/var/log/nginx/ransomware.access.log"
        ;;
    data)
        log_file="/var/log/nginx/data.access.log"
        ;;
    *)
        echo "Invalid log type. Use 'api', 'ransomware', or 'data'."
        exit 1
        ;;
esac

local_ipv6=$(ip -6 addr show | grep -oP '(?<=inet6 )[a-f0-9:]+(?=/56 scope global)' | grep -v '^fe80')

if $rss_option; then
    ips_with_count=$(grep rss.xml "$log_file" | awk '{print $1}' | sort | uniq -c)
else
    ips_with_count=$(awk '{print $1}' "$log_file" | sort | uniq -c) 
fi

# Sorting IPs by occurrence
if [ -z "$local_ipv6" ]; then
    sorted_ips=$(echo "$ips_with_count" | sort -nr)
else 
    sorted_ips=$(echo "$ips_with_count" | sort -nr | grep -v "$local_ipv6")
fi
# Process IPs based on options
process_ips

