# Gitlab admins changings
This option means getting Gtilab admins statuses every 30 min.

On the server which will get Gtilab admins statuses:

1. mv get_gitlab_admins.py /usr/local/bin
2. mv get_gitlab_admins.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_gitlab_admins.py
4. chown root:root /usr/local/bin/get_gitlab_admins.sh
5. chmod +x /usr/local/bin/get_gitlab_admins.sh
6. mkdir /var/log/gitlab
7. make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/gitlab/differences_admins.json</location>
  </localfile>
</agent_config>
```
7. cronatb -e
8. add lines:
```
*/30 * * * * sudo bash -c "/usr/local/bin/get_gitlab_admins.sh"
```

# Gitlab runners
This option means getting Gtilab runners statuses every 30 min.

On the server which will get Gtilab admins statuses:

1. mv get_gitlab_runners.py /usr/local/bin
2. mv get_gitlab_runners.sh /usr/local/bin
3. chown root:root /usr/local/bin/get_gitlab_runners.py
4. chown root:root /usr/local/bin/get_gitlab_runners.sh
5. chmod +x /usr/local/bin/get_gitlab_runners.sh
6. mkdir /var/log/gitlab
7. make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/gitlab/runners.json</location>
  </localfile>
</agent_config>
```
7. cronatb -e
8. add lines:
```
*/30 * * * * sudo bash -c "/usr/local/bin/get_gitlab_runners.sh"
```
