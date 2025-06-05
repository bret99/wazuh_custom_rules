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
```xml
<agent_config>
	<localfile>
		<log_format>json</log_format>
		<location>/var/log/nuclei/report.json</location>
	</localfile>
</agent_config>
```
7. cronatb -e
8. add lines:
```
0 21 * * * sudo bash -c "/root/go/bin/nuclei -ut;/root/go/bin/nuclei -up"
0 22 * * * sudo bash -c "/root/get_nuclei_scan.sh"
```
