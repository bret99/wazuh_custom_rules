cd /usr/local/bin
python3 get_jira_secrets_mail_alert.py
cat /usr/local/bin/jira_secrets_info.txt | mail -s "Secrets found in Jira " -r "wazuh.agent@example.com" ismonitoring@example.com # Substitute mail      s to actual ones
