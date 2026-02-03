Unsupported OS vulnerabilities

This option means unsupported OS (RedOS, Alt) vulnerabilities collection every saturday.


On Wazuh agent:
```
dnf install -y trivy jq # (RedOS)
apt-get install -y trivy jq # (Alt)
mv get_os_vulns_redos.sh /usr/local/bin # (RedOS)
mv get_os_vulns_alt.sh /usr/local/bin # (Alt)
chmod +x /usr/local/bin/get_os_vulns_redos.sh # (RedOS)
chmod +x /usr/local/bin/get_os_vulns_alt.sh # (Alt)
crontab -e
```
add line:
```
0 0 * * 6 /usr/local/bin/get_os_vulns_redos.sh # (RedOS)
0 0 * * 6 /usr/local/bin/get_os_vulns_alt.sh # (Alt)
```

On Wazuh manager:
```
/var/ossec/bin/agent_groups -a -g unsupported_os
/var/ossec/bin/agent_groups -a -g unsupported_os -i [agent.id]
```
add lines to /var/ossec/etc/share/unsupported_os/agent.conf
```
<agent_config>
  <localfile>
    <location>/var/log/vulns.json</location>
    <log_format>json</log_format>
  </localfile>
</agent_config>
```
```
vi /var/ossec/etc/rules/local_rules.xml
```
add lines:
```
<group name="unsupported_os_vulns,">
  <rule id="100101" level="3">
    <decoded_as>json</decoded_as>
    <field name="VulnerabilityID">\.+</field>
    <field name="PkgName">\.+</field>
    <options>no_full_log</options>
    <description>$(VulnerabilityID) affects $(PkgName).</description>
  </rule>
</group>
```
```
sudo systemctl restart wazuh-manager
sudo /var/ossec/bin/./agent_control -R -u [agent.id]
```
