cd /usr/local/bin
python3 get_confluence_secrets_mail_alert.py
cat /usr/local/bin/confluence_secrets_info.txt | mail -s "Потенциальные утечки в ИС Общества [Confluence] " -r "wazuh.agent@example.com" ismonitoring@example.com # Substitute mails to actual ones
