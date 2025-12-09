#!/bin/bash

# Script to collect Wazuh user events and to analize using AI model
# Run: ./soc_ai_user.sh <username> <days> [--end-date YYYY-MM-DD] [--case-sensitive]

# Minimal args checking
if [ $# -lt 2 ]; then
    echo "Run: $0 <username> <days> [--end-date ГГГГ-ММ-ДД] [--case-sensitive]"
    echo ""
    echo "Примеры:"
    echo "  $0 john.doe 7"
    echo "  $0 'DOMAIN\\john.doe' 30"
    echo "  $0 administrator 14 --end-date 2024-01-31"
    echo "  $0 Admin 1 --case-sensitive"
    echo ""
    echo "Params:"
    echo "  username        - username to search"
    echo "  days            - days to analize"
    echo "  --end-date      - optional, end date in format YYYY-MM-DD"
    echo "  --case-sensitive - optional"
    exit 1
fi

USERNAME="$1"
DAYS="$2"
shift 2

PYTHON_ARGS="$@"

echo "=============================================="
echo "Wazuh events collecting"
echo "=============================================="
echo "User: $USERNAME"
echo "Period: $DAYS days"
echo "Дополнительные параметры: $PYTHON_ARGS"
echo "Дата запуска: $(date)"
echo "=============================================="

# 1. Генерируем безопасное имя файла на основе параметров
SAFE_USERNAME=$(echo "$USERNAME" | sed 's/[^a-zA-Z0-9._-]/_/g')
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="/tmp/wazuh_events_user_${SAFE_USERNAME}_${DAYS}days_${TIMESTAMP}.json"

echo "Run Python script to collect events..."
echo "python3 /usr/local/bin/get_user_events.py \"$USERNAME\" $DAYS $PYTHON_ARGS"

if python3 /usr/local/bin/get_user_events.py "$USERNAME" $DAYS $PYTHON_ARGS; then
    GENERATED_FILE=$(ls -t /tmp/wazuh_events_user_${SAFE_USERNAME}_*.json 2>/dev/null | head -1)

    if [ -z "$GENERATED_FILE" ] || [ ! -f "$GENERATED_FILE" ]; then
        echo "Error: report file not found"

        GENERATED_FILE=$(ls -t /tmp/wazuh_events_user_*.json 2>/dev/null | head -1)
        if [ -z "$GENERATED_FILE" ] || [ ! -f "$GENERATED_FILE" ]; then
            echo "report file not found. Fifnishing running."
            exit 1
        fi
        echo "Alternative file found: $GENERATED_FILE"
    fi

    cp "$GENERATED_FILE" "$REPORT_FILE"
    echo "Using report file: $REPORT_FILE"

    echo "Sending report file to host with AI model..."
    ansible -i /usr/local/bin/hosts ai_server -m copy -a "src=$REPORT_FILE dest=$REPORT_FILE" -b -v

    echo "Run AI analize at remote host..."
    ansible -i /usr/local/bin/hosts ai_server -m command -a "python3 /usr/local/bin/soc_ai_v2.py --mode ueba --file $REPORT_FILE" -b -v

    echo "Temporary files deleting..."

    ansible -i /usr/local/bin/hosts ai_server -m file -a "path=$REPORT_FILE state=absent" -b -v
    
    rm -f "$REPORT_FILE"
    
    if [ -f "$GENERATED_FILE" ] && [ "$GENERATED_FILE" != "$REPORT_FILE" ]; then
        rm -f "$GENERATED_FILE"
    fi

    echo "=============================================="
    echo "AI analize successful!"
    echo "=============================================="

else
    echo "Python script run error"
    exit 1
fi
