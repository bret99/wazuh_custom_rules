# Directum files downloadings

Add to agent.conf to Wazuh agent at Directum server the next:
```xml
<agent_config>
  <localfile>
    <location>C:\inetpub\logs\DrxWeb\hostname.WebServer.%Y-%m-%d.log</location> <!-- Substitute log file path to actual one --> 
    <log_format>json</log_format>
  </localfile>
</agent_config>
```
