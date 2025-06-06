# Proxmox VMs

This option means getting Proxmox VMs statuses every 30 min.

On the server which will get Proxmox VMs statuses:
```
mv get_proxmox_vms.py /usr/local/bin
mv get_proxmox_vms.sh /usr/local/bin
chown root:root /usr/local/bin/get_proxmox_vms.py
chown root:root /usr/local/bin/get_proxmox_vms.sh
chmod +x /usr/local/bin/get_proxmox_vms.sh
mkdir /var/log/proxmox
```
make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/proxmox/vm_info.json</location>
  </localfile>
</agent_config>
```
```
cronatb -e
```
add line:
```
*/30 * * * * sudo bash -c "/usr/local/bin/get_proxmox_vms.sh"
```
