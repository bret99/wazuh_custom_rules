# Nuclei scan

This option means getting Nuclei scan every 24 hours.

On the server which will get web sites statuses:

install nuclei
```
mv get_nuclei_scan.py /usr/local/bin
mv get_nuclei_scan.sh /usr/local/bin
chown root:root /usr/local/bin/get_nuclei_scan.py
chown root:root /usr/local/bin/get_nuclei_scan.sh
chmod +x /usr/local/bin/get_nuclei_scan.sh
mkdir /var/log/nuclei
```
make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/nuclei/report.json</location>
  </localfile>
</agent_config>
```
```
cronatb -e
```
add lines:
```
0 21 * * * sudo bash -c "/root/go/bin/nuclei -ut;/root/go/bin/nuclei -up"
0 22 * * * sudo bash -c "/root/get_nuclei_scan.sh"
```
