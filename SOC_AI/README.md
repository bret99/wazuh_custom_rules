# Make SOC report

Getting every hour SOC report to email, VK Teams, Telegram. One should keep in mind that one should uncomment respective lines in soc_ai_py.

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
