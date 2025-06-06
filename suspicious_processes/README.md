Suspiciuos processes

This option means a presence of a server (with Wazuh agent preinstalled) which should get Wazuh agents processes using Wazuh API every 5 minutes.


On Wazuh manager:
```
mv get_agents_processes.py /usr/local/bin
mv get_lolbas.py /usr/local/bin
mv get_agents_processes.sh /usr/local/bin
mv get_lolbas.py /usr/local/bin
mv get_lolbas.sh /usr/local/bin
mv processes.txt /usr/local/bin
chown root:root get_agents_processes.sh
chmod +x get_agents_processes.sh
chown root:root get_lolbas.sh
chmod +x get_lolbas.sh
mv secret_tokens.py /usr/local/bin
mv gtfobins.txt /usr/local/bin
cronatb -e
```
add lines:
```
0 0 * * * sudo bash -c "/usr/local/bin/get_lolbas.sh"
*/5 * * * * sudo bash -c "/usr/local/bin/get_agents_processes.sh"
```
