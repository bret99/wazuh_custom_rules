# Jira tasks
Prerequisite:
Jira user account should be synchronized to Active Directory and have Jira admin rights. 

Scenario №1 [get full Jira tasks content for all Jira events every 6 hours]

On Wazuh-manager:

1. mv get_jira_tasks.py /usr/local/bin && chown root:root /usr/local/bin/get_jira_tasks.py
2. mv secret_tokens.py /usr/local/bin
3. mv get_jira_tasks.sh /usr/local/bin && chown root:root /usr/local/bin/get_jira_tasks.sh && chmod +x /usr/local/bin/get_jira_tasks.sh
4. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<!-- Shared agent configuration here -->
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/jira/tasks.json</location>
	</localfile>
</agent_config>

4. add host with preinstalled wazuh agent to the group from 3rd point
5. crontab -e
6. add:

0 1 * * * sudo bash -c "/usr/local/bin/get_jira_tasks.sh"

0 7 * * * sudo bash -c "/usr/local/bin/get_jira_tasks.sh"

0 13 * * * sudo bash -c "/usr/local/bin/get_jira_tasks.sh"

0 19 * * * sudo bash -c "/usr/local/bin/get_jira_tasks.sh"

Scenario №2 [get Jira tasks generation alerts and full jira tasks content only for found secrets every 6 hours]

On Wazuh-manager:

1. mv get_jira_tasks2.py /usr/local/bin && chown root:root /usr/local/bin/get_jira_tasks2.py
2. mv secret_tokens.py /usr/local/bin
3. mv get_jira_tasks2.sh /usr/local/bin && chown root:root /usr/local/bin/get_jira_tasks2.sh && chmod +x /usr/local/bin/get_jira_tasks2.sh
4. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<!-- Shared agent configuration here -->
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/jira/tasks.json</location>
	</localfile>
</agent_config>

4. add host with preinstalled wazuh agent to the group from 3rd point
5. crontab -e
6. add:

0 1 * * * sudo bash -c "/usr/local/bin/get_jira_tasks2.sh"

0 7 * * * sudo bash -c "/usr/local/bin/get_jira_tasks2.sh"

0 13 * * * sudo bash -c "/usr/local/bin/get_jira_tasks2.sh"

0 19 * * * sudo bash -c "/usr/local/bin/get_jira_tasks2.sh"


# Confluence tasks
Prerequisite:
Confluence user account should be synchronized to Active Directory and have Confluence admin rights.

Scenario №1 [get full Confluence tasks content for all Confluence events every 6 hours]

On Wazuh-manager:

1. mv get_confluence_tasks.py /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks.py
2. mv secret_tokens.py /usr/local/bin
3. mv get_confluence_tasks.sh /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks.sh && chmod +x /usr/local/bin/get_confluence_tasks.sh
4. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<!-- Shared agent configuration here -->
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/confluence/tasks.json</location>
	</localfile>
</agent_config>

4. add host with preinstalled wazuh agent to the group from 3rd point
5. crontab -e
6. add:

0 1 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks.sh"

0 7 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks.sh"

0 13 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks.sh"

0 19 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks.sh"

Scenario №2 [get Confluence tasks generation alerts and full Confluence tasks content only for found secrets every 6 hours]

On Wazuh-manager:

1. mv get_confluence_tasks2.py /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks2.py
2. mv secret_tokens.py /usr/local/bin
3. mv get_confluence_tasks2.sh /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks2.sh && chmod +x /usr/local/bin/get_confluence_tasks2.sh
4. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<!-- Shared agent configuration here -->
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/confluence/tasks.json</location>
	</localfile>
</agent_config>

4. add host with preinstalled wazuh agent to the group from 3rd point
5. crontab -e
6. add:

0 1 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks2.sh"

0 7 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks2.sh"

0 13 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks2.sh"

0 19 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks2.sh"

# Malware IPs
One should get malware IPs list from source one prefer and move this list to /var/ossec/etc/lists/malware_ips. Do not forget add ":" to the end of each line and restart wazuh-manager.

# OpenVPN and Cisco connections
For groups "cisco" and "openvpn_corp" one should substitute values to actual in lines with respectve comments.

# Connections from not corporate hosts
On Wazuh-manager:

1. mv get_ad_hostnames.py /usr/local/bin && chown root:root /usr/local/bin/get_ad_hostnames.py
2. mv get_ad_hostnames.sh /usr/local/bin && chown root:root /usr/local/bin/get_ad_hostnames.sh && chmod +x /usr/local/bin/get_ad_hostnames.sh
3. crontab -e
4. add:

0 0 * * * sudo bash -c "/usr/local/bin/get_ad_hostnames.sh"

0 12 * * * sudo bash -c "/usr/local/bin/get_ad_hostnames.sh"

   
# OpenVPN connections

Scenario №1 [without AbuseIPDB, IP2location API integration]

For group "openvpn_status" one should make the next on Wazuh-manager:

1. mv get_openvpn_users_connections.py /usr/local/bin && chown root:root /usr/local/get_openvpn_users_connections.py
2. mv get_openvpn_users_connections.sh /usr/local/bin && chown root:root /usr/local/bin/get_openvpn_users_connections.sh && chmod +x /usr/local/bin/get_openvpn_users_connections.sh
3. substitute path to OpenVPN connections log (not syslog) to actual one

4. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/openvpn/users_connections.json</location>
	</localfile>
</agent_config>

5. add host with preinstalled wazuh agent to the group from 3rd point
6. crontab -e
7. add:

*/5 * * * * sudo bash -c "/usr/local/bin/get_openvpn_users_connections.sh"

Scenario №2 [with AbuseIPDB, IP2location API integration]

For group "openvpn_status" one should make the next on Wazuh-manager:

1. mv get_openvpn_users_connections2.py /usr/local/bin && chown root:root /usr/local/get_openvpn_users_connections2.py
2. mv get_openvpn_users_connections2.sh /usr/local/bin && chown root:root /usr/local/bin/get_openvpn_users_connections2.sh && chmod +x /usr/local/bin/get_openvpn_users_connections2.sh
3. substitute path to OpenVPN connections log (not syslog) to actual one

4. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/openvpn/users_connections.json</location>
	</localfile>
</agent_config>

5. add host with preinstalled wazuh agent to the group from 3rd point
6. crontab -e
7. add:

*/5 * * * * sudo bash -c "/usr/local/bin/get_openvpn_users_connections2.sh"

# Mail alerts for found secrets in Jira and Confluence tasks
This option will allow to get alerts if any of list "secret_tokens" in secret_tokens.py is in Jira/Confluence tasks for 24 hours.

On Wazuh-manager:

1. preconfigure postfix
2. mv secret_tokens.py /usr/local/bin
3. mv get_jira_secrets_mail_alert.py /usr/local/bin
4. mv get_confluence_secrets_mail_alert.py /usr/local/bin
5. mv get_jira_secrets_mail_alert.sh /usr/local/bin
6. mv get_confluence_secrets_mail_alert.sh /usr/local/bin
7. chown root:root /usr/local/bin/get_jira_secrets_mail_alert.sh
8. chown root:root /usr/local/bin/get_confluence_secrets_mail_alert.sh
9. mv secret_tokens.py /usr/local/bin
10. substitute mails in get_jira_secrets_mail_alert.sh and get_confluence_secrets_mail_alert.sh to actual ones
11. cronatb -e
12. add:

0 12 * * * sudo bash -c "/usr/local/bin/get_jira_secrets_mail_alert.sh"

0 11 * * * sudo bash -c "/usr/local/bin/get_confluence_secrets_mail_alert.sh"

# Suspiciuos processes
This option means a presence of a server (with Wazuh agent preinstalled) which should get Wazuh agents processes using Wazuh API every 5 minutes.

On server:

1. mv get_wazuh_agents_processes.py /usr/local/bin
2. mv get_lolbas.py /usr/local/bin
3. mv get_wazuh_agents_processes.sh /usr/local/bin
4. mv get_lolbas.py /usr/local/bin
5. mv get_lolbas.sh /usr/local/bin
6. mv processes.txt /usr/local/bin
7. chown root:root get_wazuh_agents_processes.sh
8. chmod +x get_wazuh_agents_processes.sh
9. chown root:root get_lolbas.sh
8. chmod +x get_lolbas.sh
10. mv secret_tokens.py /usr/local/bin
11. mv gtfobins.txt /usr/local/bin
12. cronatb -e
13. add:

0 0 * * * sudo bash -c "/usr/local/bin/get_lolbas.sh"
*/5 * * * * sudo bash -c "/usr/local/bin/get_wazuh_agents_processes.sh"
