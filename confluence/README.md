# Confluence tasks

Prerequisite: Confluence user account should be synchronized to Active Directory and have Confluence admin rights.

Scenario №1 [get full Confluence tasks content for all Confluence events every 6 hours]

On Wazuh-manager:
```
mv get_confluence_tasks.py /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks.py
mv secret_tokens.py /usr/local/bin
mv get_confluence_tasks.sh /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks.sh && chmod +x /usr/local/bin/get_confluence_tasks.sh
```    
make Wazuh agents group called as one like and add the next lines to agent.conf:

```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/confluence/tasks.json</location>
  <localfile>
</agent_config>
```
add host with preinstalled wazuh agent to the group from 3rd point
```
crontab -e
```
add:
```
0 1 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks.sh"
0 7 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks.sh"
0 13 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks.sh"
0 19 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks.sh"
```
Scenario №2 [get Confluence tasks generation alerts and full Confluence tasks content only for found secrets every 6 hours]

On Wazuh-manager:
```
mv get_confluence_tasks_2.py /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks_2.py
mv secret_tokens.py /usr/local/bin
mv get_confluence_tasks_2.sh /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks_2.sh && chmod +x /usr/local/bin/get_confluence_tasks_2.sh
```
make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/confluence/tasks.json</location>
  </localfile>
</agent_config>
```
add host with preinstalled wazuh agent to the group from 3rd point
```
crontab -e
```
add line:
```
0 1 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks_2.sh"
```
# Mail alerts for found secrets in Confluence tasks

This option will allow to get alerts if any of list "secret_tokens" in secret_tokens.py is in Confluence tasks for 24 hours.

On Wazuh-manager:

preconfigure postfix
```
mv secret_tokens.py /usr/local/bin
mv get_confluence_secrets_mail_alert.py /usr/local/bin
mv get_confluence_secrets_mail_alert.sh /usr/local/bin
chown root:root /usr/local/bin/get_confluence_secrets_mail_alert.sh
mv secret_tokens.py /usr/local/bin
```
substitute mails in get_confluence_secrets_mail_alert.sh for actual ones
```
cronatb -e
```
add lines:
```
0 11 * * * sudo bash -c "/usr/local/bin/get_confluence_secrets_mail_alert.sh"
0 7 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks_2.sh"
0 13 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks_2.sh"
0 19 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks_2.sh"
```
