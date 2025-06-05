# Corporate code possible leakage

Check keyword findings in repositories and code in github.com, gitlab.com, hub.docker.com.

This option means getting check statuses at 5 AM.

On the server which will get check statuses:
```
mv get_secret_dockerhub_repo_yesterday.py /usr/local/bin
mv get_secret_github_repo_yesterday.py /usr/local/bin
mv get_secret_github.py /usr/local/bin
mv get_secret_dockerhub_repo.py /usr/local/bin
mv get_secret_gitlab.py /usr/local/bin
mv get_secret_gitlab_repo.py /usr/local/bin
mv get_secret_gitlab_repo_yesterday.py /usr/local/bin
mv get_secret_github_repo.py /usr/local/bin
mv get_corp_code_leakage.sh /usr/local/bin
chown root:root get_secret_dockerhub_repo_yesterday.py
chown root:root get_secret_github_repo_yesterday.py
chown root:root get_secret_github.py
chown root:root get_secret_dockerhub_repo.py
chown root:root get_secret_gitlab.py
chown root:root get_secret_gitlab_repo.p
chown root:root get_secret_gitlab_repo_yesterday.py
chown root:root get_secret_github_repo.py
chmod +x /usr/local/bin/get_corp_code_leakage.sh
mkdir /var/log/corp_code
```
Make Wazuh agents group called as one like and add the next lines to agent.conf:
```xml
<agent_config>
  <localfile>
      <log_format>json</log_format>
      <location>/var/log/corp_code/dockerhub_search_results.json</location>
    </localfile>
    <localfile>
      <log_format>json</log_format>
      <location>/var/log/corp_code/yesterday_updated_docker_repositories.json</location>
    </localfile>
    <localfile>
      <log_format>json</log_format>
      <location>/var/log/corp_code/github_search_results.json</location>
    </localfile>
    <localfile>
      <log_format>json</log_format>
      <location>/var/log/corp_code/github_secret_repos.json</location>
    </localfile>
    <localfile>
      <log_format>json</log_format>
      <location>/var/log/corp_code/yesterday_updated_github_repositories.json</location>
    </localfile>
    <localfile>
      <log_format>json</log_format>
      <location>/var/log/corp_code/gitlab_search_results.json</location>
    </localfile>
    <localfile>
      <log_format>json</log_format>
      <location>/var/log/corp_code/gitlab_secret_repos.json</location>
    </localfile>
    <localfile>
      <log_format>json</log_format>
      <location>/var/log/corp_code/yesterday_updated_gitlab_repositories.json</location>
    </localfile>
</agent_config>
```
7. cronatb -e
8. add lines:
```
0 5 * * * sudo bash -c "/usr/local/bin/get_corp_code_leakage.sh"
```

