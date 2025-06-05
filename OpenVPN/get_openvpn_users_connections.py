import json
import os

# Substitute connections log file to actual
os.system("cat /var/log/openvpn/status.log | awk '{print $1}' | head -n -3 | tail -n +4 | sed 's/ROUTING//;s/Virtual//' | sed '/^$/d' > /root/input.txt")

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
os.system("mv /root/differences.json /var/log/openvpn/users_connections.json")
