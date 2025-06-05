# Kaspersky Security Center events

1. Configure Kaspersky Security Center to send CEF logs to SIEM (Wazuh manager IP)
2. configure target Kaspersky Security Center policy to send events tto SIEM
3. Add to Wazuh manager ossec.conf:
 <!-- KSC events -->
```xml  
  <remote>
    <connection>syslog</connection>
    <port>514</port>
    <protocol>udp</protocol>
    <allowed-ips>10.10.10.10/32</allowed-ips> <!-- Substitute Kaspersky server IP [10.10.10.10] to actual one -->
    <local_ip>192.168.10.10</local_ip> <!-- Substitute Wazuh manager IP [192.168.10.10] to actual one -->
  </remote>
```

