# Bitrix file downloadings

Add to agent.conf to Wazuh agent at Bitrix server the next:
```xml
<agent_config>
  <localfile>
    <location>/var/log/nginx/portal_access.log</location>
    <log_format>syslog</log_format>
  </localfile>
</agent_config>
```
