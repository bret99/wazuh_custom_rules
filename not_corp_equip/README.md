# Domain connections from not corporate equipment
This option means getting Active Directory valid accounts every 6 hours.

Add to <ruleset> section in /var/ossec/etc/ossec.conf line:
```xml
<list>etc/lists/ad_hostnames</list>
```

On Wazuh-manager:
```
mv get_ad_hosts.py /usr/local/bin
mv get_ad_hosts.sh /usr/local/bin
chown root:root /usr/local/bin/get_ad_hosts.py
chown root:root /usr/local/bin/get_ad_hosts.sh
chmod +x /usr/local/bin/get_ad_hosts.sh
cronatb -e
```
add lines:
```
0 0 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"
0 6 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"
0 12 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"
0 18 * * * sudo bash -c "/usr/local/bin/get_ad_hosts.sh"
```
```
sudo systemctl restart wazuh-manager
```
# Send email to user that shared confidential information
On Wazuh manager:
```
mv send_email_equip.py /usr/local/bin
chmod +x /usr/local/bin/send_email_equip.py
chown /usr/local/bin/send_email_equip.py
crontab -e
```
add lines:
```
*/5 * * * * sudo bash -c "python3 /usr/local/bin/send_email_equip.py"
```
