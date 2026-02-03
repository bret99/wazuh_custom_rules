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
