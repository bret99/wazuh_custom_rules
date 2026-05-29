#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration / API Keys
LOG_FILE="/var/log/openvp/users_connections.json"
IP2LOCATION_KEY="" # insert here actual IP2Location API key
ABUSEIPDB_KEY=""  # insert here actual AbuseIPDB API key

# Ensure log file exists and is writable
if [ ! -w "$(dirname "$LOG_FILE")" ] && [ ! -w "$LOG_FILE" ]; then
    echo "Error: Cannot write to $LOG_FILE" >&2
    exit 1
fi

# 1. ip2location check
IP2LOCATION_RESP=$(curl --silent --max-time 10 --fail "https://api.ip2location.io/?key=${IP2LOCATION_KEY}&ip=46.39.234.27&format=json" || true)

if echo "$IP2LOCATION_RESP" | grep -q '"city_name"'; then
    echo '{"ip2location_api_response":"accessable"}' >> "$LOG_FILE"
else
    echo '{"ip2location_api_response":"unaccessable"}' >> "$LOG_FILE"
fi

# 2. abuseipdb check
ABUSEIPDB_RESP=$(curl --silent --max-time 10 --fail "https://api.abuseipdb.com/api/v2/check?ipAddress=11.15.161.13&maxAgeInDays=90&verbose" \
    -H "Key: ${ABUSEIPDB_KEY}" \
    -H "Accept: application/json" || true)

if echo "$ABUSEIPDB_RESP" | grep -q '"countryName"'; then
    echo '{"abuseipdb_api_response":"accessable"}' >> "$LOG_FILE"
else
    echo '{"abuseipdb_api_response":"unaccessable"}' >> "$LOG_FILE"
fi
