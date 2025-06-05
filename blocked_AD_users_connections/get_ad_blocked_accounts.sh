cd /usr/local/bin
python3 get_ad_blocked_accounts.py

if [ ! -s "/var/ossec/etc/lists/ad_disabled_accounts_prev" ]; then
    echo "The file /var/ossec/etc/lists/ad_disabled_accounts is empty or does not exist. Exiting script."
    exit 1
fi

mv /var/ossec/etc/lists/ad_disabled_accounts_prev /var/ossec/etc/lists/ad_disabled_accounts
sed -i 's/$/:/' /var/ossec/etc/lists/ad_disabled_accounts
cat /var/ossec/etc/lists/ad_disabled_accounts | tr '[:lower:]' '[:upper:]' > /var/ossec/etc/lists/ad_disabled_accounts_upper
cat /var/ossec/etc/lists/ad_disabled_accounts_upper | tr '[:upper:]' '[:lower:]' > /var/ossec/etc/lists/ad_disabled_accounts_lower
cat /var/ossec/etc/lists/ad_disabled_accounts_upper > /var/ossec/etc/lists/ad_disabled_accounts
cat /var/ossec/etc/lists/ad_disabled_accounts_lower >> /var/ossec/etc/lists/ad_disabled_accounts
rm -f /var/ossec/etc/lists/ad_disabled_accounts_upper
rm -f /var/ossec/etc/lists/ad_disabled_accounts_lower
chown root:root /var/ossec/etc/lists/ad_disabled_accounts
systemctl restart wazuh-manager
