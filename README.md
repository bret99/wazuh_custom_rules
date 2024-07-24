# Jira tasks
Prerequisite:
Jira user account should be synchronized to Active Directory and have Jira admin rights. 


1. mv get_jira_tasks.py /usr/local/bin && chown root:root /usr/local/bin/get_jira_tasks.py
2. mv secret_tokens.py /usr/local/bin
3. mv get_jira_tasks.sh /usr/local/bin && chown root:root /usr/local/bin/get_jira_tasks.sh && chmod +x /usr/local/bin/get_jira_tasks.sh
4. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<!-- Shared agent configuration here -->
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/suricata/eve.json</location>
	</localfile>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/jira/tasks.json</location>
	</localfile>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/confluence/tasks.json</location>
	</localfile>
</agent_config>

4. add host with preinstalled wazuh agent to the group from 3rd point.
   
# Confluence tasks
Prerequisite:
Jira user account should be synchronized to Active Directory and have Jira admin rights.


1. mv get_confluence_tasks.py /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks.py
2. mv secret_tokens.py /usr/local/bin
3. mv get_confluence_tasks.sh /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks.sh && chmod +x /usr/local/bin/get_confluence_tasks.sh
4. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<!-- Shared agent configuration here -->
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/suricata/eve.json</location>
	</localfile>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/jira/tasks.json</location>
	</localfile>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/confluence/tasks.json</location>
	</localfile>
</agent_config>

4. add host with preinstalled wazuh agent to the group from 3rd point.
   
# Malware IPs
One should get malware IPs list from source one prefer and move this list to /var/ossec/etc/lists/malware_ips. Do not forget add ":" to the end of each line and restart wazuh-manager.

# OpenVPN and Cisco connections
For groups "cisco" and "openvpn_corp" one should substitute values to actual in lines with respectve comments.

# Connections from not corporate hosts
1. mv get_ad_hostnames.py /usr/local/bin && chown root:root /usr/local/bin/get_ad_hostnames.py
2. mv get_ad_hostnames.sh /usr/local/bin && chown root:root /usr/local/bin/get_ad_hostnames.sh && chmod +x /usr/local/bin/get_ad_hostnames.sh
   
# OpenVPN connections
For group "openvpn_status" one should make the next:
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

5. add host with preinstalled wazuh agent to the group from 3rd point.

# Mail alerts for found secrets in Jira and Confluence tasks
This option will allow to get alerts if any of list "secret_tokens" in secret_tokens.py is in Jira/Confluence tasks.

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

