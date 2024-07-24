cd /usr/local/bin
python3 get_ad_hostnames.py > /var/ossec/etc/lists/ad_hostnames
sed -i 's/$/:/' /var/ossec/etc/lists/ad_hostnames
cat /var/ossec/etc/lists/ad_hostnames | tr '[:lower:]' '[:upper:]' > /var/ossec/etc/lists/ad_hostnames_upper
cat /var/ossec/etc/lists/ad_hostnames_upper | tr '[:upper:]' '[:lower:]' > /var/ossec/etc/lists/ad_hostnames_lower
cat /var/ossec/etc/lists/ad_hostnames_upper > /var/ossec/etc/lists/ad_hostnames
cat /var/ossec/etc/lists/ad_hostnames_lower >> /var/ossec/etc/lists/ad_hostnames
rm -f /var/ossec/etc/lists/ad_hostnames_upper
rm -f /var/ossec/etc/lists/ad_hostnames_lower
chown root:root /var/ossec/etc/lists/ad_hostnames
systemctl restart wazuh-manager
