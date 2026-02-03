Agents network exposure

This option means agents syscollector information collection every 3 hours.

On Wazuh manager:
```
sudo mv get_agents_netaddr.sh /var/ossec/bin/get_agents_netaddr.sh
sudo mv get_agents_netaddr_ansible.sh /var/ossec/bin/get_agents_netaddr_abnsible.sh
sudo chmod+x /var/ossec/bin/get_agents_netaddr.sh
sudo chmod +x /var/ossec/bin/get_agents_netaddr_abnsible.sh
sudo chown root:root /var/ossec/bin/get_agents_netaddr.sh
sudo chown root:root /var/ossec/bin/get_agents_netaddr_abnsible.sh
sudo /var/ossec/bin/agent_groups -a -g agents_network_exposure
sudo /var/ossec/bin/agent_groups -a -g agents_network_exposure -i [agent.id]
sudo crontab -e
```
add line:
0 */3 * * * sudo bash -c "/var/ossec/bin/get_agents_netaddr_abnsible.sh"
```
vi /var/ossec/etc/share/agents_network_exposure/agent.conf
```
add lines:
```
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/agents_netaddr_report.json</location>
  </localfile>
</agent_config>
```
```
sudo /var/ossec/bin/./agent_control -R -u [agent.id]
```
```
vi /var/ossec/etc/rules/local_rules.xml
```
add lines:
```
<group name="network_exposure,">
  <rule id="100101" level="11">
    <decoded_as>json</decoded_as>
    <field name="agent.agent_name">\.+</field>
    <field name="agent.interfaces">\.+</field>
    <options>no_full_log</options>
    <mitre>
      <id>T1040</id>
      <id>T1590.001</id>
      <id>T1053.002</id>
      <id>T1040</id>
    </mitre>
    <description>Host $(agent.agent_name) has public interface $(agent.interfaces).</description>
    <group>network_exposure,pci_dss_1.3.1,pci_dss_11.4.4,pci_dss_12.10.1,nist_800_53_SC.7,nist_800_53_SC.8,nist_800_53_AU.6,nist_800_53_SI.4,gdpr_IV_32.2,gdpr_IV_35.7.d,tsc_CC6.6,tsc_CC6.7,tsc_CC7.2,tsc_CC7.3</group>
  </rule>
</group>
```
