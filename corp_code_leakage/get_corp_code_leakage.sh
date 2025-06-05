cd /usr/local/bin

rm -f /var/log/corp_code/*.json
# Get Github corporate code
python3 get_secret_github.py
jq -c '.[]' github_search_results.json > /var/log/corp_code/github_search_results.json
rm -f github_search_results.json
sleep 60

python3 get_secret_github_repo.py
jq -c '.[]' github_secret_repos.json > /var/log/corp_code/github_secret_repos.json
rm -f github_secret_repos.json
sleep 60

python3 get_secret_github_repo_yesterday.py
jq -c '.[]' yesterday_updated_github_repositories.json > /var/log/corp_code/yesterday_updated_github_repositories.json
rm -f yesterday_updated_github_repositories.json
sleep 60

# Get Docker Hub corporate code
python3 get_secret_dockerhub_repo.py
jq -c '.[]' dockerhub_search_results.json > /var/log/corp_code/dockerhub_search_results.json
rm -f dockerhub_search_results.json
sleep 60

python3 get_secret_dockerhub_repo_yesterday.py
jq -c '.[]' yesterday_updated_docker_repositories.json > /var/log/corp_code/yesterday_updated_docker_repositories.json
rm -f yesterday_updated_docker_repositories.json
sleep 60

# Get Gitlab corporate code
python3 get_secret_gitlab.py
jq -c '.[]' gitlab_search_results.json > /var/log/corp_code/gitlab_search_results.json
rm -f gitlab_search_results.json
sleep 60

python3 get_secret_gitlab_repo.py
jq -c '.[]' gitlab_secret_repos.json > /var/log/corp_code/gitlab_secret_repos.json
rm -f gitlab_secret_repos.json
sleep 60

python3 get_secret_gitlab_repo_yesterday.py
jq -c '.[]' yesterday_updated_gitlab_repositories.json > /var/log/corp_code/yesterday_updated_gitlab_repositories.json
rm -f yesterday_updated_gitlab_repositories.json
sleep 60

