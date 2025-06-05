# Bitrix file downloadings

Add to agent.conf to Wazuh agent at Bitrix server the next:
```xml
<agent_config>
  <localfile>
    <location>/var/log/nginx/bitrix_access.log</location> <!-- Substitute log file path to actual one --> 
    <log_format>syslog</log_format>
  </localfile>
</agent_config>
```
