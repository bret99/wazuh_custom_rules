import os
import json
import requests
from secret_tokens import abuseipdb_token, ip2location_token

# Substitute log file to actual one
os.system("cat /var/log/openvpn/status.log | awk '{print $1}' | head -n -3 | tail -n +4 | sed 's/ROUTING//;s/Virtual//' | sed '/^$/d' > /root/input.txt")

def get_abuse_info(ip_address):
    api_key = abuseipdb_token
    url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip_address}&maxAgeInDays=90&verbose"
    headers = {
        "Key": api_key,
        "Accept": "application/json"
    }
    try:
        # Fetch AbuseIPDB data
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()["data"]
        abuse_info = {
            "abuesIPDB.isPublic": data["isPublic"],
            "abuesIPDB.usage_type": data["usageType"],
            "abuesIPDB.isp": data["isp"],
            "abuesIPDB.abuseConfidenceScore": data["abuseConfidenceScore"],
            "abuesIPDB.countryName": data["countryName"],
            "abuesIPDB.domain": data["domain"],
            "abuesIPDB.isTor": data["isTor"]
        }
    except requests.exceptions.RequestException as e:
        abuse_info = {
            "abuesIPDB.isPublic": "null",
            "abuesIPDB.usage_type": "null",
            "abuesIPDB.isp": "null",
            "abuesIPDB.abuseConfidenceScore": "null",
            "abuesIPDB.countryName": "null",
            "abuesIPDB.domain": "null",
            "abuesIPDB.isTor": "null"
        }
    try:
        # Fetch IP2Location data only if the first request was successful
        ip2location_url = f"https://api.ip2location.io/?key={ip2location_token}&ip={ip_address}&format=json"
        ip2location_response = requests.get(ip2location_url)
        ip2location_response.raise_for_status()
        ip2location_data = ip2location_response.json()
        abuse_info.update({
            "ip2location.countryCode": ip2location_data["country_code"],
            "ip2location.countryName": ip2location_data["country_name"],
            "ip2location.regionName": ip2location_data["region_name"],
            "ip2location.cityName": ip2location_data["city_name"],
            "ip2location.latitude": ip2location_data["latitude"],
            "ip2location.longitude": ip2location_data["longitude"],
            "ip2location.as": ip2location_data["as"],
            "ip2location.asn": ip2location_data["asn"],
            "ip2location.zipCode": ip2location_data["zip_code"],
            "ip2location.timeZone": ip2location_data["time_zone"]
        })
    except requests.exceptions.RequestException as e:
        # Optionally handle errors for IP2Location, but this won't overwrite existing data
        abuse_info.update({
#        ip2location_data = {
            "ip2location.countryCode": "null",
            "ip2location.countryName": "null",
            "ip2location.regionName": "null",
            "ip2location.cityName": "null",
            "ip2location.latitude": "null",
            "ip2location.longitude": "null",
            "ip2location.as": "null",
            "ip2location.asn": "null",
            "ip2location.zipCode": "null",
            "ip2location.timeZone": "null"
#        }
        })
    return abuse_info


def parse_line(line):
    fields = line.strip().split(',')
    if len(fields) == 4:
        return {
            "dstip": fields[0],
            "srcuser": fields[1],
            "srcip": fields[2].split(':')[0],
            "srcport": fields[2].split(':')[1],
            "timestamp": fields[3]
        }
    else:
        return None

with open('/root/input.txt', 'r') as file:
    lines = file.readlines()

data = []
for line in lines:
    parsed_line = parse_line(line)
    if parsed_line:
        complete_line = {
            "dst_ip": parsed_line.get("dstip", ""),
            "src_user": parsed_line.get("srcuser", ""),
            "srcip": parsed_line.get("srcip", ""),
            "src_port": parsed_line.get("srcport", ""),
            "timestamp": parsed_line.get("timestamp", "")
        }
        data.append(complete_line)

with open('output_1.json', 'w') as file:
    for item in data:
        json.dump(item, file)
        file.write('\n')

with open('output.json', 'r') as f1, open('output_1.json', 'r') as f2:
    data1 = [json.loads(line) for line in f1]
    data2 = [json.loads(line) for line in f2]
src_user_ips = {}
for item in data1:
    src_user = item['src_user']
    src_ip = item['srcip']
    if src_user in src_user_ips:
        src_user_ips[src_user].add(src_ip)
    else:
        src_user_ips[src_user] = set([src_ip])

differences = []
for item in data2:
    src_user = item['src_user']
    src_ip = item['srcip']
    if src_user not in src_user_ips or src_ip not in src_user_ips[src_user]:
        # Get the additional information from the AbuseIPDB and IP2Location APIs
        abuse_info = get_abuse_info(src_ip)
        if abuse_info:
            item.update(abuse_info)
        differences.append(item)

with open('differences.json', 'w') as f3:
    if differences:
        for item in differences:
            json.dump(item, f3)
            f3.write('\n')
    else:
        print("")

os.system("rm -f /root/input.txt")
os.system("mv /root/output_1.json /root/output.json")
os.system("cat /root/differences.json > /var/log/openvpn/users_connections.json")
