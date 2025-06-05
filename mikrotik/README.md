# Mikrotik

1. Configure your Mikrotik to send ipsec errors and log in events to Wazuh server
2. copy custom Mikrotik rules and decoders to your ones
3. add to Wazuh manager ossec.conf:
 <!-- Mikrotik events -->
```xml  
  <remote>
    <connection>syslog</connection>
    <port>514</port>
    <protocol>udp</protocol>
    <allowed-ips>10.10.10.10/32</allowed-ips> <!-- Substitute Mikrotik IP [10.10.10.10] to actual one -->
    <local_ip>192.168.10.10</local_ip> <!-- Substitute Wazuh manager IP [192.168.10.10] to actual one -->
  </remote>
```

