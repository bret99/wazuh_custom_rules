# Blocked Active Directory accounts connections detection
This option means getting Active Directory blocked accounts every 12 hours.

On Wazuh-manager:

1. mv get_ad_blocked_accounts.py /usr/local/bin
2. mv get_ad_blocked_accounts.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_ad_blocked_accounts.py
4. chown root:root /usr/local/bin/get_ad_blocked_accounts.sh
5. chmod +x /usr/local/bin/get_ad_blocked_accounts.sh
6. cronatb -e
7. add:
```
0 0 * * * sudo bash -c "/usr/local/bin/get_ad_blocked_accounts.sh"
0 12 * * * sudo bash -c "/usr/local/bin/get_ad_blocked_accounts.sh"
```
