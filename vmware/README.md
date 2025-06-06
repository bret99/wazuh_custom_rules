# VMWare VMs
This option means getting VMWare VMs statuses every hour.

On the server which will get VMs statuses:
```
mv get_vmware_vms.py /usr/local/bin
mv get_vmware_vms.py.sh /usr/local/bin
chown root:root /usr/local/bin/get_vmware_vms.py
chown root:root /usr/local/bin/get_vmware_vms.sh
chmod +x /usr/local/bin/get_vmware_vms.sh
mkdir /var/log/vdc
```
make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/vdc/previous_vms.json</location>
  </localfile>
</agent_config>
```
```
cronatb -e
```
add line:
```
0 * * * * sudo bash -c "/usr/local/bin/get_vmware_vms.py.sh"
```
