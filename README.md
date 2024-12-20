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

1. mv get_jira_tasks_2.py /usr/local/bin && chown root:root /usr/local/bin/get_jira_tasks_2.py
2. mv secret_tokens.py /usr/local/bin
3. mv get_jira_tasks_2.sh /usr/local/bin && chown root:root /usr/local/bin/get_jira_tasks_2.sh && chmod +x /usr/local/bin/get_jira_tasks_2.sh
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

0 1 * * * sudo bash -c "/usr/local/bin/get_jira_tasks_2.sh"

0 7 * * * sudo bash -c "/usr/local/bin/get_jira_tasks_2.sh"

0 13 * * * sudo bash -c "/usr/local/bin/get_jira_tasks_2.sh"

0 19 * * * sudo bash -c "/usr/local/bin/get_jira_tasks_2.sh"


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

1. mv get_confluence_tasks_2.py /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks_2.py
2. mv secret_tokens.py /usr/local/bin
3. mv get_confluence_tasks_2.sh /usr/local/bin && chown root:root /usr/local/bin/get_confluence_tasks_2.sh && chmod +x /usr/local/bin/get_confluence_tasks_2.sh
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

0 1 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks_2.sh"

0 7 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks_2.sh"

0 13 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks_2.sh"

0 19 * * * sudo bash -c "/usr/local/bin/get_confluence_tasks_2.sh"

# Malware IPs
One should get malware IPs list from source one prefer and move this list to /var/ossec/etc/lists/malware_ips. Do not forget add ":" to the end of each line and restart wazuh-manager.

# OpenVPN and Cisco connections
For groups "cisco" and "openvpn_corp" one should substitute values to actual in lines with respectve comments.

# Connections from not corporate hosts
On Wazuh-manager:

1. mv get_ad_hosts.py /usr/local/bin && chown root:root /usr/local/bin/get_ad_hosts.py
2. mv get_ad_hosts.sh /usr/local/bin && chown root:root /usr/local/bin/get_ad_hosts.sh && chmod +x /usr/local/bin/get_ad_hosts.sh
3. crontab -e
4. add:

0 0 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"

0 12 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"

   
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

1. mv get_openvpn_users_connections_2.py /usr/local/bin && chown root:root /usr/local/get_openvpn_users_connections_2.py
2. mv get_openvpn_users_connections_2.sh /usr/local/bin && chown root:root /usr/local/bin/get_openvpn_users_connections_2.sh && chmod +x /usr/local/bin/get_openvpn_users_connections_2.sh
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

*/5 * * * * sudo bash -c "/usr/local/bin/get_openvpn_users_connections_2.sh"

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

1. mv get_agents_processes.py /usr/local/bin
2. mv get_lolbas.py /usr/local/bin
3. mv get_agents_processes.sh /usr/local/bin
4. mv get_lolbas.py /usr/local/bin
5. mv get_lolbas.sh /usr/local/bin
6. mv processes.txt /usr/local/bin
7. chown root:root get_agents_processes.sh
8. chmod +x get_agents_processes.sh
9. chown root:root get_lolbas.sh
8. chmod +x get_lolbas.sh
10. mv secret_tokens.py /usr/local/bin
11. mv gtfobins.txt /usr/local/bin
12. cronatb -e
13. add:

0 0 * * * sudo bash -c "/usr/local/bin/get_lolbas.sh"

*/5 * * * * sudo bash -c "/usr/local/bin/get_agents_processes.sh"

# Domain connections from not corporate equipment
This option means getting Active Directory valid accounts every 6 hours.

On Wazuh-manager:

1. mv get_ad_hosts.py /usr/local/bin
2. mv get_ad_hosts.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_ad_hosts.py
4. chown root:root /usr/local/bin/get_ad_hosts.sh
5. chmod +x /usr/local/bin/get_ad_hosts.sh
6. cronatb -e
7. add:

0 0 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"

0 6 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"

0 12 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"

0 18 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"


# Blocked Active Directory accounts connections detection
This option means getting Active Directory blocked accounts every 12 hours.

On Wazuh-manager:

1. mv get_ad_blocked_accounts.py /usr/local/bin
2. mv get_ad_blocked_accounts.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_ad_blocked_accounts.py
4. chown root:root /usr/local/bin/get_ad_blocked_accounts.sh
5. chmod +x /usr/local/bin/get_ad_blocked_accounts.sh
6. cronatb -e
7. add:

0 0 * * * sudo bash -c "/usr/local/bin/get_ad_blocked_accounts.sh"

0 12 * * * sudo bash -c "/usr/local/bin/get_ad_blocked_accounts.sh"

# VMWare VMs
This option means getting VMWare VMs statuses every hour.

On the server which will get VMs statuses:

1. mv get_vmware_vms.py /usr/local/bin
2. mv get_vmware_vms.py.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_vmware_vms.py
4. chown root:root /usr/local/bin/get_vmware_vms.sh
5. chmod +x /usr/local/bin/get_vmware_vms.sh
6. mkdir /var/log/vdc
7. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/vdc/previous_vms.json</location>
	</localfile>
	<localfile>
        	<log_format>json</log_format>
        	<location>/var/log/vdc/differences_vms.json</location>
    </localfile>
</agent_config>

7. cronatb -e
8. add:

0 * * * * sudo bash -c "/usr/local/bin/get_vmware_vms.py.sh"

# Gitlab admins changings
This option means getting Gtilab admins statuses statuses every 30 min.

On the server which will get Gtilab admins statuses:

1. mv get_gitlab_admins.py /usr/local/bin
2. mv get_gitlab_admins.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_gitlab_admins.py
4. chown root:root /usr/local/bin/get_gitlab_admins.sh
5. chmod +x /usr/local/bin/get_gitlab_admins.sh
6. mkdir /var/log/gitlab
7. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/gitlab/differences_admins.json</location>
	</localfile>
</agent_config>

7. cronatb -e
8. add:

*/30 * * * * sudo bash -c "/usr/local/bin/get_gitlab_admins.sh"

# Gitlab runners
This option means getting Gtilab runners statuses every 30 min.

On the server which will get Gtilab admins statuses:

1. mv get_gitlab_runners.py /usr/local/bin
2. mv get_gitlab_runners.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_gitlab_runners.py
4. chown root:root /usr/local/bin/get_gitlab_runners.sh
5. chmod +x /usr/local/bin/get_gitlab_runners.sh
6. mkdir /var/log/gitlab
7. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/gitlab/runners.json</location>
	</localfile>
</agent_config>

7. cronatb -e
8. add:

*/30 * * * * sudo bash -c "/usr/local/bin/get_gitlab_runners.sh"

# Proxmox VMs

This option means getting Proxmox VMs statuses every 30 min.

On the server which will get Proxmox VMs statuses:

1. mv get_proxmox_vms.py /usr/local/bin
2. mv get_proxmox_vms.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_proxmox_vms.py
4. chown root:root /usr/local/bin/get_proxmox_vms.sh
5. chmod +x /usr/local/bin/get_proxmox_vms.sh
6. mkdir /var/log/proxmox
7. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/proxmox/vm_info.json</location>
	</localfile>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/proxmox/vm_differences.json</location>
	</localfile>
</agent_config>

7. cronatb -e
8. add:

*/30 * * * * sudo bash -c "/usr/local/bin/get_proxmox_vms.sh"

# Nuclei scan

This option means getting Nuclei scan every 24 hours.

On the server which will get web sites statuses:

1. install nuclei
2. mv nuclei-templates /usr/local/bin
3. mv get_nuclei_scan.py /usr/local/bin
4. mv get_nuclei_scan.sh /usr/local/bin
5. chown root:root /usr/local/bin/get_nuclei_scan.py
6. chown root:root /usr/local/bin/get_nuclei_scan.sh
7. chmod +x /usr/local/bin/get_nuclei_scan.sh
8. mkdir /var/log/nuclei
9. make Wazuh agents group called as one like and add the next lines to agent.conf:

<agent_config>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/nuclei/report.json</location>
	</localfile>
</agent_config>

7. cronatb -e
8. add:

0 21 * * * sudo bash -c "/root/go/bin/nuclei -ut;/root/go/bin/nuclei -up"
0 22 * * * sudo bash -c "/root/get_nuclei_scan.sh"
