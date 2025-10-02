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
*/5 * * * * sudo bash -c "/usr/local/bin/get_openvpn_users_connections.sh"
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
*/5 * * * * sudo bash -c "/usr/local/bin/get_openvpn_users_connections_2.sh"
```
# Raw OpenVPN connections

One should add to agent.conf at OpenVPN server with Wazuh agent the next strings:
```xml
<agent_config>
  <localfile>
    <log_format>syslog</log_format>
    <location>/var/log/openvpn/status*.log</location> # Change if necessary
  </localfile>    
</agent_config>
```
# Send email to user with foreign connection

```
crontab -e
```
add lines:
```
*/10 * * * * sudo bash -c "python3 /usr/local/bin/send_email_openvpn.py"
```

# Important

One should make CDB lists cities.cdb (to detect foreign connections) and dch_providers.cdb (to detect hosting connections). Those ones should be got from ip2location DBs. Also one should substitute country code to actual one in group "openvpn_foreign" at local_rules.xml
