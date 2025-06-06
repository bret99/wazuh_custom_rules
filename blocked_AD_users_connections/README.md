# Blocked Active Directory accounts connections detection
This option means getting Active Directory blocked accounts every 12 hours.
Add to section in /var/ossec/etc/ossec.conf line:
```xml
 <list>etc/lists/ad_disabled_accounts</list>
```
On Wazuh-manager:
```
mv get_ad_blocked_accounts.py /usr/local/bin
mv get_ad_blocked_accounts.sh /usr/local/bin
chown root:root /usr/local/bin/get_ad_blocked_accounts.py
chown root:root /usr/local/bin/get_ad_blocked_accounts.sh
chmod +x /usr/local/bin/get_ad_blocked_accounts.sh
cronatb -e
```
add lines:
```
0 0 * * * sudo bash -c "/usr/local/bin/get_ad_blocked_accounts.sh"
0 12 * * * sudo bash -c "/usr/local/bin/get_ad_blocked_accounts.sh"
```
```
sudo systemctl restart wazuh-manager
```
