#!/bin/bash

# Delete previous report
ansible -i /usr/local/bin/hosts some_host -m file -a "path=/var/log/agents_netaddr_report.json state=absent" -b -v # subsitute "some_host" to actual one that present at ansible hosts file

# Run remote script to get json report
/var/ossec/bin/get_agents_netaddr.sh

# Get final report at remote SIEM node
cat /tmp/agents_netaddr_report.json | grep -vE '172\\.14\\.' | jq -c 'select(.agent.interfaces[].iface | length > 0)' > /tmp/agents_netaddr_report_final.json -b -v

# Copy report from remote SIEM node
ansible -i /usr/local/bin/hosts some_host -m fetch -a "src=/tmp/agents_netaddr_report_final.json dest=/tmp/agents_netaddr_report.json flat=yes" -v # subsitute "some_host" to actual one that present at ansible hosts file

# Send report to some_host
ansible -i /usr/local/bin/hosts some_host -m copy -a "src=/tmp/agents_netaddr_report.json dest=/var/log/agents_netaddr_report.json" -b -v # subsitute "some_host" to actual one that present at ansible hosts file

# Deleting report files
ansible -i /usr/local/bin/hosts some_host -m file -a "path=/tmp/agents_netaddr_report.json state=absent" -b -v # subsitute "some_host" to actual one that present at ansible hosts file
ansible -i /usr/local/bin/hosts some_host -m file -a "path=/tmp/agents_netaddr_report_final.json state=absent" -b -v # subsitute "some_host" to actual one that present at ansible hosts file
rm -f /tmp/agents_netaddr_report.json
