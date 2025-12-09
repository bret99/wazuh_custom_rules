# Run script to get json report
python3 /usr/local/bin/get_hour_opensearch_events.py

# Send report to host with AI model
ansible -i /usr/local/bin/hosts ai_server -m copy -a "src=/tmp/wazuh_events_level3_10.json dest=/tmp/wazuh_events_level3_10.json" -b -v # wazuh_events_level3_10.json is value of LOG_FILE in secret_tokens.py

# Run remote script with AI model
ansible -i /usr/local/bin/hosts ai_server -m command -a "python3 /usr/local/bin/soc_ai.py /tmp/wazuh_events_level3_10.json" -b -v # wazuh_events_level3_10.json is value of LOG_FILE in secret_tokens.py
# ansible -i /usr/local/bin/hosts ai_server -m command -a "python3 /usr/local/bin/soc_ai_v2.py --mode global --file /tmp/wazuh_events_level3_10.json" -b -v # run this one to deal with version 2 (upgraded with EMEBEDDINGS)

# Deleting report files
ansible -i /usr/local/bin/hosts ai_server -m file -a "path=/tmp/wazuh_events_level3_10.json state=absent" -b -v # wazuh_events_level3_10.json is value of LOG_FILE in secret_tokens.py
rm -f /tmp/wazuh_events_level3_10.json # wazuh_events_level3_10.json is value of LOG_FILE in secret_tokens.py
