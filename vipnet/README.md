# Vipnet

Run commands on target Vipnet coordinator:
1. firewall local add src 10.10.10.10 dst 192.168.10.10 udp dport 514 pass # Substitute coordinator IP [10.10.10.10] and Wazuh manager IP [192.168.10.10] to actual ones
2. machine set loghost 192.168.10.10 # Substitute Wazuh manager IP [192.168.10.10] to actual one
3. add to Wazuh manager ossec.conf:
 <!-- Vipnet coordinator events -->
```xml  
  <remote>
    <connection>syslog</connection>
    <port>514</port>
    <protocol>udp</protocol>
    <allowed-ips>10.10.10.10/32</allowed-ips> <!-- Substitute Vipnet coordinator IP [10.10.10.10] to actual one -->
    <local_ip>192.168.10.10</local_ip> <!-- Substitute Wazuh manager IP [192.168.10.10] to actual one -->
  </remote>
```
