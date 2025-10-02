# Make SOC report

Getting every hour SOC report to email, VK Teams, Telegram.

Architecture:
1. getting alerts with rule.level between 3 and 10 on Wazuh manager;
2. send json report file to AI server (see "hosts"; substitute value '192.168.10.11' for actual one);
3. run remotely script with AI that generates final reports (email, VK Teams, Telegram).
   
One should keep in mind the next:
1. uncomment lines in soc_ai.py to send short report to VK Teams and/or Telegram;
2. prepare ssh connection from Wazuh-manager to AI server via ansible;
3. one may exclude events with rule.id, rule.groups from reports using exclusions secret_tokens.py.

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
mv soc_ai.py /usr/local/bin
chown root:root /usr/local/bin/soc_ai.py
```
