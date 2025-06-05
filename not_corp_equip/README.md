# Domain connections from not corporate equipment
This option means getting Active Directory valid accounts every 6 hours.

On Wazuh-manager:

1. mv get_ad_hosts.py /usr/local/bin
2. mv get_ad_hosts.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_ad_hosts.py
4. chown root:root /usr/local/bin/get_ad_hosts.sh
5. chmod +x /usr/local/bin/get_ad_hosts.sh
6. cronatb -e
7. add lines:
```
0 0 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"
0 6 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"
0 12 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"
0 18 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"
```
