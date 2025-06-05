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
```xml
<agent_config>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/proxmox/vm_info.json</location>
	</localfile>
```
7. cronatb -e
8. add lines:
```
*/30 * * * * sudo bash -c "/usr/local/bin/get_proxmox_vms.sh"
```
