#!/usr/bin/env python3
import requests
import json
import time
import sys
import argparse
from datetime import datetime, timedelta
from secret_tokens import KEYWORD_IN_NAME


def parse_arguments():
    parser = argparse.ArgumentParser(description='Script for searching repositories at Docker Hub')
    parser.add_argument('query', nargs='?', default=KEYWORD_IN_NAME, 
                        help='Search request')
    parser.add_argument('output_file', nargs='?', default=None,
                        help='Report file name JSON yesterday_updated_docker_repositories.json")')
    parser.add_argument('--yesterday', action='store_true', default=True,
                        help='Filter only repositories updated yesterday (on by default)')
    parser.add_argument('--no-filter', dest='yesterday', action='store_false',
                        help='Deactivate date of update option')
    
    args = parser.parse_args()
    
    if args.output_file is None:
        prefix = "yesterday_updated_" if args.yesterday else ""
        args.output_file = f"{prefix}_docker_repositories.json"
    
    return args

def get_repositories_from_api(query, page=1, page_size=25):
    url = "https://hub.docker.com/v2/search/repositories/"
    params = {
        "query": query,
        "page": page,
        "page_size": page_size
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    
    except Exception as e:
        print(f"Page request error {page}: {e}")
        return {"count": 0, "results": []}

def parse_repo_name(repo_name):
    if '/' in repo_name:
        return repo_name.split('/', 1)
    return "", repo_name

def is_updated_yesterday(date_str):
    if not date_str:
        return False
    
    try:
        today = datetime.now()
        
        yesterday = today - timedelta(days=1)
        
        updated_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        yesterday_utc = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return (updated_date.year == yesterday.year and 
                updated_date.month == yesterday.month and 
                updated_date.day == yesterday.day)
    except Exception as e:
        print(f"Date calculating error {date_str}: {e}")
        return False

def get_repository_details(owner, name):
    url = f"https://hub.docker.com/v2/repositories/{owner}/{name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Repository details requst error {owner}/{name}: {e}")
        return None

def get_all_repositories(query, filter_yesterday=True):
    all_repositories = []
    filtered_repositories = []
    page = 1
    total_count = None
    page_size = 25
    
    today = datetime.now()
    
    yesterday = today - timedelta(days=1)
    
    print(f"Today: {today.strftime('%Y-%m-%d')}")
    print(f"Yesterday: {yesterday.strftime('%Y-%m-%d')}")
    
    while True:
        print(f"Getting page {page}...")
        response_data = get_repositories_from_api(query, page, page_size)
        
        if total_count is None:
            total_count = response_data.get("count", 0)
            print(f"Found repositories: {total_count}")
        
        results = response_data.get("results", [])
        if not results:
            break
            
        for repo in results:
            repo_name = repo.get("repo_name", "")
            owner, name = parse_repo_name(repo_name)
            
            repo_owner = repo.get("repo_owner", "")
            if not repo_owner:
                repo_owner = owner
            
            print(f"Repository details getting {repo_owner}/{name}...")
            details = get_repository_details(repo_owner, name)
            
            if details:
                last_updated = details.get("last_updated", "")
                
                repository_info = {
                    "repo_name": name,
                    "repo_owner": repo_owner,
                    "repo_description": repo.get("short_description", "") or details.get("description", ""),
                    "repo_url": f"https://hub.docker.com/r/{repo_name}",
                    "repo_pull_count": repo.get("pull_count", 0),
                    "repo_star_count": repo.get("star_count", 0),
                    "repo_is_official": repo.get("is_official", False),
                    "repo_is_automated": repo.get("is_automated", False),
                    "repo_last_updated": last_updated
                }
                
                if filter_yesterday:
                    if is_updated_yesterday(last_updated):
                        filtered_repositories.append(repository_info)
                        print(f"Repository {repo_owner}/{repo_name} updated yesterday ({last_updated})!")
                    else:
                        print(f"Repository {repo_owner}/{repo_name} updated not yesterday ({last_updated}), ignoring.")
                else:
                    all_repositories.append(repository_info)
            
            time.sleep(0.5)
        
        print(f"Repositories {len(results)} processed at {page}")
        
        if len(all_repositories) + len(filtered_repositories) >= total_count or len(results) < page_size:
            break
            
        page += 1
        time.sleep(0.5)
    
    return filtered_repositories if filter_yesterday else all_repositories

def main():
    args = parse_arguments()
    query = args.query
    output_file = args.output_file
    filter_yesterday = args.yesterday
    
    filter_msg = "with yesterday updating filtration" if filter_yesterday else "without date filtration"
    print(f"Starting of script Docker Hub repositories searching for request '{query}' {filter_msg}...")
    
    repositories = get_all_repositories(query, filter_yesterday)
    
    print(f"Collected repositories: {len(repositories)}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(repositories, f, indent=2, ensure_ascii=False)
    
    print(f"Results are saved to {output_file}")
    
if __name__ == "__main__":
    main()

