# Gitlab admins changings
This option means getting Gtilab admins statuses every 30 min.

On the server which will get Gtilab admins statuses:
```
mv get_gitlab_admins.py /usr/local/bin
mv get_gitlab_admins.sh /usr/local/bin
chown root:root /usr/local/bin/get_gitlab_admins.py
chown root:root /usr/local/bin/get_gitlab_admins.sh
chmod +x /usr/local/bin/get_gitlab_admins.sh
mkdir /var/log/gitlab
```
make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/gitlab/differences_admins.json</location>
  </localfile>
</agent_config>
```
```
cronatb -e
```
add lines:
```
*/30 * * * * sudo bash -c "/usr/local/bin/get_gitlab_admins.sh"
```

# Gitlab runners
This option means getting Gtilab runners statuses every 30 min.

On the server which will get Gtilab admins statuses:
```
mv get_gitlab_runners.py /usr/local/bin
mv get_gitlab_runners.sh /usr/local/bin
chown root:root /usr/local/bin/get_gitlab_runners.py
chown root:root /usr/local/bin/get_gitlab_runners.sh
chmod +x /usr/local/bin/get_gitlab_runners.sh
mkdir /var/log/gitlab
```
make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
    <log_format>json</log_format>
    <location>/var/log/gitlab/runners.json</location>
  </localfile>
</agent_config>
```
```
cronatb -e
```
add lines:
```
*/30 * * * * sudo bash -c "/usr/local/bin/get_gitlab_runners.sh"
```
