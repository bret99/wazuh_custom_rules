# Corporate code possible leakage

Check keyword findings in repositories and code in github.com, gitlab.com, hub.docker.com.

This option means getting check statuses at 5 AM.

On the server which will get check statuses:

1. mv get_secret_dockerhub_repo_yesterday.py /usr/local/bin
2. mv get_secret_github_repo_yesterday.py /usr/local/bin
3. mv get_secret_github.py /usr/local/bin
4. mv get_secret_dockerhub_repo.py /usr/local/bin
5. mv get_secret_gitlab.py /usr/local/bin
6. mv get_secret_gitlab_repo.py /usr/local/bin
7. mv get_secret_gitlab_repo_yesterday.py /usr/local/bin
8. mv get_secret_github_repo.py /usr/local/bin
9. mv get_corp_code_leakage.sh /usr/local/bin
10. chown root:root get_secret_dockerhub_repo_yesterday.py
11. chown root:root get_secret_github_repo_yesterday.py
12. chown root:root get_secret_github.py
13. chown root:root get_secret_dockerhub_repo.py
14. chown root:root get_secret_gitlab.py
15. chown root:root get_secret_gitlab_repo.p
16. chown root:root get_secret_gitlab_repo_yesterday.py
17. chown root:root get_secret_github_repo.py
18. chmod +x /usr/local/bin/get_corp_code_leakage.sh
19. mkdir /var/log/corp_code
20. make Wazuh agents group called as one like and add the next lines to agent.conf:
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

