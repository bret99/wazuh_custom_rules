# VK Teams integration
Scenario №1

1. Create new bot using VK Teams "metabot"
2. copy created bot token ```example: 001.0159988340.1712388373:1011569394```
3. create new channel
4. copy created channel ID ```example: tryhFDvAnQSWGZ12sjI. This is a subsequence of chars after "https://myteam.mail.ru/profile/" ```
5. add bot to the channel with admin rights
   
On Wazuh manager:
```
mv custom-vkteams /var/ossec/integrations
mv custom-vkteams.py /var/ossec/integrations
chmod +x /var/ossec/integrations/custom-vkteams*
chown root:wazuh /var/ossec/integrations/custom-vkteams*
```
add to /var/ossec/etc/ossec.conf:
```xml
<!-- VK Teams integration -->
<integration>
  <name>custom-vkteams</name>
  <hook_url>https://api.internal.myteam.mail.ru/bot/v1/messages/sendText</hook_url>
  <level>11</level> <!-- Change the level to value one prefer -->
  <alert_format>json</alert_format>
</integration>
```
insert actual bot token and channel ID to custom-vkteams.py
```
sudo systemctl restart wazuh-manager
```
Scenario №2
# Send alerts to VK Teams with rule.level between 11 and higher
On Wazuh manager:
```
mv send_vkteams_opensearch_events.py /usr/local/bin
chmod +x /usr/local/bin/send_vkteams_opensearch_events.py
chown /usr/local/bin/send_vkteams_opensearch_events.py
crontab -e
```
add lines:
```
*/3 * * * * sudo bash -c "python3 /usr/local/bin/send_vkteams_opensearch_events.py"
```
