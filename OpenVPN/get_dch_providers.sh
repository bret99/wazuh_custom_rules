#!/usr/bin/env bash
set -euo pipefail

# --- Configuration ---
readonly DB_CODE="PX6" # substitute for actual one (https://www.ip2location.com/file-download#!free-database) 
readonly API_TOKEN="" # substitute for actual one (https://www.ip2location.com/file-download#!free-database)
readonly API_URL="https://www.ip2location.com/download?token=${API_TOKEN}&file=${DB_CODE}LITECSV"
readonly ZIP_NAME="IP2PROXY-LITE-${DB_CODE}.CSV.zip"
readonly CSV_NAME="IP2PROXY-LITE-${DB_CODE}.CSV"
readonly OUT_FILE="dch_providers.txt"
readonly TARGET_PATH="/var/ossec/etc/lists/dch_providers"

# --- Force include / exclude lists ---
FORCE_INCLUDE=("example.com" "test.com") # substitute for actual one
FORCE_EXCLUDE=("something.com", "somewhere.com") # substitute for actual one

# --- Temporary workspace ---
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

cd "$TMPDIR"

# --- Download ---
curl -fsSL -o "$ZIP_NAME" "$API_URL"

# --- Unzip ---
unzip -q "$ZIP_NAME"

# --- Validate extracted file exists ---
if [[ ! -f "$CSV_NAME" ]]; then
    echo "ERROR: $CSV_NAME not found after extraction" >&2
    exit 1
fi

# --- Extract DCH provider domains from CSV ---
# CSV fields: 1=ip_from, 2=ip_to, 3=proxy_type, 4=country_code, 5=country_name,
#             6=region_name, 7=city_name, 8=isp, 9=domain, 10=usage_type
# Filter: field 10 == "DCH", field 9 must contain a dot (valid domain)
RAW_FILE="raw_domains.txt"
awk -F',' '
    $10 == "\"DCH\"" {
        gsub(/"/, "", $9)
        if ($9 ~ /\./) print $9
    }
' "$CSV_NAME" | sort -u > "$RAW_FILE"

# --- Apply exclusions ---
FILTERED_FILE="filtered_domains.txt"
if [[ ${#FORCE_EXCLUDE[@]} -gt 0 ]]; then
    grep -vF -f <(printf '%s\n' "${FORCE_EXCLUDE[@]}") "$RAW_FILE" > "$FILTERED_FILE"
else
    cp "$RAW_FILE" "$FILTERED_FILE"
fi

# --- Apply inclusions ---
{
    cat "$FILTERED_FILE"
    printf '%s\n' "${FORCE_INCLUDE[@]}"
} | sort -u | sed 's/$/:/' > "$OUT_FILE"

# --- Validate output file before moving ---
if [[ ! -f "$OUT_FILE" ]]; then
    echo "ERROR: $OUT_FILE was not created" >&2
    exit 1
fi

if [[ ! -s "$OUT_FILE" ]]; then
    echo "ERROR: $OUT_FILE is empty, aborting move to $TARGET_PATH" >&2
    exit 1
fi

# --- Move to target ---
mv "$OUT_FILE" "$TARGET_PATH"

echo "Done: $TARGET_PATH updated"
