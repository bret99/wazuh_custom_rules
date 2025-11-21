# Collect browsing history

Windows hosts

1. copy create_scheduled_tasks.bat, systeminfo.vbs, systeminfocollect.bat to target host
2. run with high privileges cmd.exe
3. enter the folder with files from point 1
4. run .\create_scheduled_tasks.bat

One may use centralized method to run those ones (KSC for instatnce).

On Wazuh manager:

make Wazuh agents group called as one like and add the next lines to agent.conf:

```xml
<agent_config>
  <syscheck>
      <directories check_all="yes" report_changes="yes" realtime="yes">C:\tools</directories>
      <directories check_all="yes" report_changes="yes" realtime="yes">C:\Windows\systeminfo.vbs</directories>
      <directories check_all="yes" report_changes="yes" realtime="yes">C:\Windows\systeminfocollect.bat</directories>
      <directories check_all="yes" report_changes="yes" realtime="yes">C:\Windows\Temp\SystemInfoCollect\*_history.json</directories>   
  </syscheck>
  <localfile>
      <location>C:\Windows\Temp\SystemInfoCollect\*.json</location>
      <log_format>json</log_format>
  </localfile>
</agent_config>
```

Linux hosts

copy install_dependencies.sh, install_browser_history_service.sh, systeminfocollect.py to target host
```
chmod +x install_dependencies.sh
chmod +x install_browser_history_service.sh
./install_dependencies.sh
./install_browser_history_service.sh
```

One may use centralized method to run those ones (KSC for instatnce).

On Wazuh manager:

make Wazuh agents group called as one like and add the next lines to agent.conf:

```xml
<agent_config>
  <syscheck>
      <directories check_all="yes" realtime="yes" whodata="yes">/opt/systeminfocollect</directories>
      <directories check_all="yes" realtime="yes" whodata="yes">/var/log/systeminfocollect.json</directories>
  </syscheck>
  <localfile>
     <location>/var/log/systeminfocollect.json</location>
     <log_format>json</log_format> 
  </localfile>
</agent_config>
```
