# Usergate

1. Configure Usergate to send target logs to Wazuh manager in CEF
2. add to Wazuh manager ossec.conf:
 <!-- Usergate events -->
```xml  
  <remote>
    <connection>syslog</connection>
    <port>514</port>
    <protocol>udp</protocol>
    <allowed-ips>10.10.10.10/32</allowed-ips> <!-- Substitute Usergate IP [10.10.10.10] to actual one -->
    <local_ip>192.168.10.10</local_ip> <!-- Substitute Wazuh manager IP [192.168.10.10] to actual one -->
  </remote>
```
