# Make SOC report

Getting every hour SOC report to email, VK Teams, Telegram.

Architecture:
1. getting alerts with rule.level between 3 and 10 on Wazuh manager;
2. send json report file to AI server (see "hosts"; substitute value '192.168.10.11' for actual one);
3. run remotely script with AI that generates final reports (email, VK Teams, Telegram).

One should keep in mind the next:
1. uncomment lines in soc_ai.py to send short report to VK Teams and/or Telegram;
2. prepare ssh connection from Wazuh-manager to AI server via ansible;
3. one may exclude events with rule.id, rule.groups from reports using exclusions in secret_tokens.py;
4. one may substitute 'Russia' for actual one in line 72 at soc_ai.py and in line 33 at soc_prompt.txt.

soc_ai.py [Version 1]

On Wazuh-manager:
```
mv get_opensearch_events.py /usr/local/bin
mv secret_tokens.py /usr/local/bin
chown root:root /usr/local/bin/get_opensearch_events.py
chown root:root /usr/local/bin/secret_tokens.py
mv soc_ai.sh /usr/local/bin
chown root:root /usr/local/bin/soc_ai.sh
chmod +x /usr/local/bin/soc_ai.sh
mv hosts /usr/local/bin/hosts
chown root:root /usr/local/bin/hosts
cronatb -e
```
add lines:
```
10 * * * * sudo bash -c "/usr/local/bin/soc_ai.sh"
```
```
sudo systemctl restart wazuh-manager
```
On SOC AI server:
```
mv soc_ai_v2.py /usr/local/bin
chown root:root /usr/local/bin/soc_ai.py
```
soc_ai_v2.py [Version 2, upgraded with embeddings]

On Wazuh-manager:
```
mv get_opensearch_events.py /usr/local/bin
mv secret_tokens.py /usr/local/bin
chown root:root /usr/local/bin/get_opensearch_events.py
chown root:root /usr/local/bin/secret_tokens.py
mv soc_ai_v2.sh /usr/local/bin
chown root:root /usr/local/bin/soc_ai_v2.sh
chmod +x /usr/local/bin/soc_ai_v2.sh
mv hosts /usr/local/bin/hosts
chown root:root /usr/local/bin/hosts
mv get_host_events.py /usr/local/bin/get_host_events.py
mv get_user_events.py /usr/local/bin/get_user_events.py
chown root:root /usr/local/bin/get_host_events.py
chown root:root /usr/local/bin/get_user_events.py
mv vk_notifier.py /usr/local/bin # only if one want to receive alerts to VK Teams
chown root:root /usr/local/bin/vk_notifier.py
cronatb -e
```
add lines:
```
10 * * * * sudo bash -c "/usr/local/bin/soc_ai_v2.sh"
```
```
sudo systemctl restart wazuh-manager
```
On SOC AI server:
```
mv soc_ai_v2.py /usr/local/bin
mv soc_prompts* /usr/local/bin
chown root:root /usr/local/bin/soc_ai_v2.py
```
To get UEBA report for concrete user
```
mv soc_ai_user.sh /usr/local/bin
chown root:root /usr/local/bin/soc_ai_user.sh
chmod +x /usr/local/bin/soc_ai_user.sh
/usr/local/bin/soc_ai_user.sh --help
```
To get deep report for concrete host
```
mv soc_ai_host.sh /usr/local/bin
chown root:root /usr/local/bin/soc_ai_host.sh
chmod +x /usr/local/bin/soc_ai_host.sh
/usr/local/bin/soc_ai_host.sh --help
```
