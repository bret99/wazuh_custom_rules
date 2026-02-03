#!/bin/bash

# Configuration
WAZUH_HOST="127.0.0.1"
USERNAME="wazuh-wui"
PASSWORD="" # Insert here actual one
API_URL="https://$WAZUH_HOST:55000"

# Get authentication token
TOKEN=$(curl -k -s -u "$USERNAME:$PASSWORD" -X GET "$API_URL/security/user/authenticate?raw=true")

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to obtain token" >&2
    exit 1
fi

# Get list of all active agents
AGENTS_JSON=$(curl -k -s -X GET "$API_URL/agents?status=active&limit=100000" -H "Authorization: Bearer $TOKEN")
AGENT_IDS=$(echo "$AGENTS_JSON" | jq -r '.data.affected_items[].id')

# Clear old report
> /tmp/agents_netaddr_report.json

for AGENT_ID in $AGENT_IDS; do
    AGENT_NAME=$(echo "$AGENTS_JSON" | jq -r ".data.affected_items[] | select(.id==\"$AGENT_ID\") | .name")

    # Get network addresses
    sleep 0.2
    NET_DATA=$(curl -k -s -X GET "$API_URL/syscollector/$AGENT_ID/netaddr?limit=1000" -H "Authorization: Bearer $TOKEN")

    # Filter reserved and private IPv4 addresses
    INTERFACES=$(echo "$NET_DATA" | jq -c '[.data.affected_items[] | select(
        .proto == "ipv4" and
        (.address | test("^(10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.|192\\.168\\.|127\\.|169\\.254\\.|100\\.(6[4-9]|[7-9][0-9]|1[0-1][0-9]|12[0-7])\\.|0\\.|22[4-9]\\.|2[3-5][0-9]\\.)") | not)
    )]')

    # FIX: Check if INTERFACES is empty/null, use "null" string if so
    if [ -z "$INTERFACES" ] || [ "$INTERFACES" = "null" ]; then
        INTERFACES='"null"'
    fi

    # Generate final report line (JSONL)
    echo "{\"agent\": {\"agent_name\": \"$AGENT_NAME\", \"interfaces\": $INTERFACES}}" >> /tmp/agents_netaddr_report.json
done
