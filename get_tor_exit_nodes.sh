#!/bin/bash

curl -s https://check.torproject.org/exit-addresses | awk '/ExitAddress/ {print $2}' | sort -n > /var/ossec/etc/lists/tor_exit_nodes
sed -i 's/$/:/' /var/ossec/etc/lists/tor_exit_nodes
chown wazuh:wazuh /var/ossec/etc/lists/tor_exit_nodes
systemctl restart wazuh-manager.service
