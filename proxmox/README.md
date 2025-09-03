# Proxmox VMs

Scenario #1

This option means getting Proxmox VMs statuses every 30 min using Proxmox API.

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
    <location>/var/log/proxmox/current.json</location>
  </localfile>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/proxmox/differences.json</location>
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


Scenario #2

This option means getting Proxmox VMs statuses every 30 min collecting reports directly on Proxmox.

On Proxmox server:
```
mv vm_monitor.sh /usr/local/bin
chown root:root /usr/local/bin/vm_monitor.sh
chmod +x /usr/local/bin/vm_monitor.sh
```

make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/previous_vms.json</location>
  </localfile>
<localfile>
    <log_format>json</log_format>
    <location>/var/log/differences_vms.json</location>
  </localfile>
</agent_config>
```
```
cronatb -e
```
add line:
```
*/30 * * * * sudo bash -c "/usr/local/bin/vm_monitor.sh"
```
