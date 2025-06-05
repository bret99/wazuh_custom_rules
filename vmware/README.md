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
```xml
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
```
7. cronatb -e
8. add lines:
```
0 * * * * sudo bash -c "/usr/local/bin/get_vmware_vms.py.sh"
```
