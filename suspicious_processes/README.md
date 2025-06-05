Suspiciuos processes

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
10. chmod +x get_lolbas.sh
11. mv secret_tokens.py /usr/local/bin
12. mv gtfobins.txt /usr/local/bin
13. cronatb -e
14. add lines:
```
0 0 * * * sudo bash -c "/usr/local/bin/get_lolbas.sh"
*/5 * * * * sudo bash -c "/usr/local/bin/get_agents_processes.sh"
```
