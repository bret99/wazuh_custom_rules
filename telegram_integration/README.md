# Telegram integration

1. Create new bot using Telegram "@BotFather"
2. copy created bot token ```example: bot4829403728:DPF9mOIscWKMPapETqe8BZSgfftap_nP9dU```
3. create new channel
4. copy created channel ID ```example: digits subsequence```
5. add bot to the channel with admin rights
   
On Wazuh manager:
```
mv custom-telegram /var/ossec/integrations
mv custom-telegram.py /var/ossec/integrations
chown root:wazuh /var/ossec/integrations/custom-telegram*
```
add to /var/ossec/etc/ossec.conf:
```xml
<!-- Telegram integration -->
<integration>
  <name>custom-telegram</name>
  <hook_url>>https://api.telegram.org/<bot_token>/sendMessage</hook_url> <!-- Substitute <bot_token> for actual one -->
  <level>11</level> <!-- Change the level to value one prefer -->
  <alert_format>json</alert_format>
</integration>
```
insert actual bot token and channel ID to custom-telegram.py
```
sudo systemctl restart wazuh-manager
```
