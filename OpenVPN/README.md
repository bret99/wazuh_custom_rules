# OpenVPN connections

Scenario №1 [without AbuseIPDB, IP2location API integration]

For group "openvpn_status" one should make the next on Wazuh-manager:
```
mv get_openvpn_users_connections.py /usr/local/bin && chown root:root /usr/local/get_openvpn_users_connections.py
mv get_openvpn_users_connections.sh /usr/local/bin && chown root:root /usr/local/bin/get_openvpn_users_connections.sh && chmod +x /usr/local/bin/get_openvpn_users_connections.sh
```
substitute path to OpenVPN connections log (not syslog) to actual one
make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/openvpn/users_connections.json</location>
  </localfile>
</agent_config>
```
add host with preinstalled wazuh agent to the group from 3rd point
```
crontab -e
```
add lines:
```
*/1 * * * * sudo bash -c "/usr/local/bin/get_openvpn_users_connections.sh" # run script every minute
```
Scenario №2 [with AbuseIPDB, IP2location API integration]

For group "openvpn_status" one should make the next on Wazuh-manager:
```
mv get_openvpn_users_connections_2.py /usr/local/bin && chown root:root /usr/local/get_openvpn_users_connections_2.py
mv get_openvpn_users_connections_2.sh /usr/local/bin && chown root:root /usr/local/bin/get_openvpn_users_connections_2.sh && chmod +x /usr/local/bin/get_openvpn_users_connections_2.sh
```
substitute path to OpenVPN connections log (not syslog) to actual one
make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/openvpn/users_connections.json</location>
  </localfile>
</agent_config>
```
add host with preinstalled wazuh agent to the group from 3rd point
```
crontab -e
```
add lines:
```
*/1 * * * * sudo bash -c "/usr/local/bin/get_openvpn_users_connections_2.sh" # run script every minute
```
# Raw OpenVPN connections

One should add to agent.conf at OpenVPN server with Wazuh agent the next strings:
```xml
<agent_config>
  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/openvpn/status*.log</location> <!-- Change if necessary -->
  </localfile>    
</agent_config>
```
# Send email to user with foreign connection
On Wazuh manager:
```
mv send_email_openvpn.py /usr/local/bin
mv secret_tokens.py /usr/local/bin
crontab -e
```
add lines:
```
*/1 * * * * sudo bash -c "python3 /usr/local/bin/send_email_openvpn.py" # run script every minute
```

# Important

One should make CDB lists cities.cdb (to detect foreign connections) and dch_providers.cdb (to detect hosting connections). Those ones should be got from ip2location DBs. Also one should substitute country code to actual one in group "openvpn_foreign" at local_rules.xml

## Check if IP2Location and AbuseIPDB API responces are accessable [optional]

For group "check_ip_api"" one should make the next on Wazuh-manager:
```
mv check_ip_api.sh /usr/local/bin && chown root:root /usr/local/check_ip_api.sh
chmod +x /usr/local/bin/check_ip_api.sh
```

make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/openvpn/users_connections.json</location>
  </localfile>
</agent_config>
```
add host with preinstalled wazuh agent to the target group
```
crontab -e
```
add lines:
```
*/1 * * * * sudo bash -c "/usr/local/bin/check_ip_api.sh" # run script every minute
```
add script to get DCH providers:
```
mv get_dch_providers.sh /usr/local/bin/
chmod +x usr/local/bin/get_dch_providers.sh
```
add task to cron:
```
crontab -e 
```
add lines:
```
0 0 * * 7 sudo bash -c "/usr/local/bin/get_dch_providers.sh" # run every sunday
```

## Get OpenVPN users sessions

add to the end of file /var/osse/ruleset/decoders/0380-windows_decoders.xml
```
<!-- OpenVPN kill command -->
<decoder name="windows-date-format-openvpn-kill">
   <parent>windows-date-format</parent>
   <type>syslog</type>
   <use_own_name>true</use_own_name>
   <prematch offset="after_parent">MANAGEMENT: CMD 'kill </prematch>
   <regex offset="after_parent">MANAGEMENT: CMD 'kill (\S+)'</regex>
   <order>dstuser</order>
</decoder>

<!-- OpenVPN SIGTERM soft,delayed-exit (IP only) -->
<decoder name="windows-date-format-openvpn-sigterm-delayed">
   <parent>windows-date-format</parent>
   <type>syslog</type>
   <use_own_name>true</use_own_name>
   <prematch offset="after_parent">\S+:\d+ SIGTERM\Ssoft,delayed-exit\S received</prematch>
   <regex offset="after_parent">(\S+):\d+ SIGTERM\Ssoft,delayed-exit\S received</regex>
   <order>srcip</order>
</decoder>

<!-- OpenVPN SIGTERM soft,remote-exit (username/IP) -->
<decoder name="windows-date-format-openvpn-sigterm-remote">
   <parent>windows-date-format</parent>
   <type>syslog</type>
   <use_own_name>true</use_own_name>
   <prematch offset="after_parent">SIGTERM\Ssoft,remote-exit\S received</prematch>
   <regex offset="after_parent">(\S+)/(\S+):\d+ SIGTERM\Ssoft,remote-exit\S received</regex>
   <order>dstuser,srcip</order>
</decoder>

<decoder name="windows-date-format-openvpn-sigterm-remote-killed">
   <parent>windows-date-format</parent>
   <type>syslog</type>
   <use_own_name>true</use_own_name>
   <prematch offset="after_parent">\S+/\S+:\d+ SIGTERM\Ssoft,\S received</prematch>
   <regex offset="after_parent">(\S+)/(\S+):\d+ SIGTERM\Ssoft,\S received</regex>
   <order>dstuser,srcip</order>
</decoder>
```
