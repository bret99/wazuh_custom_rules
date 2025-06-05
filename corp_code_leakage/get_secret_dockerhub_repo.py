#!/usr/bin/env python3
import requests
import json
import time
import sys
import argparse
from secret_tokens import KEYWORD_IN_NAME

def parse_arguments():
    parser = argparse.ArgumentParser(description='Repositories script searchig at Docker Hub')
    parser.add_argument('query', nargs='?', default=KEYWORD_IN_NAME, 
                        help='Search request')
    parser.add_argument('output_file', nargs='?', default=None,
                        help='Report file name dockerhub_search_results.json")')
    
    args = parser.parse_args()
    
    if args.output_file is None:
        args.output_file = "dockerhub_search_results.json"
    
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
        print(f"Page getting error {page}: {e}")
        return {"count": 0, "results": []}

def parse_repo_name(repo_name):
    if '/' in repo_name:
        return repo_name.split('/', 1)
    return "", repo_name

def get_all_repositories(query):
    all_repositories = []
    page = 1
    total_count = None
    page_size = 25
    
    while True:
        print(f"Page getting {page}...")
        response_data = get_repositories_from_api(query, page, page_size)
        
        if total_count is None:
            total_count = response_data.get("count", 0)
            print(f"Repositories found: {total_count}")
        
        results = response_data.get("results", [])
        if not results:
            break
            
        for repo in results:
            repo_name = repo.get("repo_name", "")
            owner, name = parse_repo_name(repo_name)
            
            repo_owner = repo.get("repo_owner", "")
            if not repo_owner:
                repo_owner = owner
                
            repository_info = {
                "repo_name": name,
                "repo_owner": repo_owner,
                "repo_description": repo.get("short_description", ""),
                "repo_url": f"https://hub.docker.com/r/{repo_name}",
                "repo_pull_count": repo.get("pull_count", 0),
                "repo_star_count": repo.get("star_count", 0),
                "repo_is_official": repo.get("is_official", False),
                "repo_is_automated": repo.get("is_automated", False)
            }
            all_repositories.append(repository_info)
        
        print(f"Found repositories {len(results)} at page {page}")
        
        if len(all_repositories) >= total_count or len(results) < page_size:
            break
            
        page += 1
        time.sleep(0.5)
    
    return all_repositories

def main():
    args = parse_arguments()
    query = args.query
    output_file = args.output_file
    
    print(f"Starting of script finding Docker Hub repositories for request '{query}'...")
    
    repositories = get_all_repositories(query)
    
    print(f"Collected repositories: {len(repositories)}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(repositories, f, indent=2, ensure_ascii=False)
    
    print(f"Results are saved to {output_file}")
    
if __name__ == "__main__":
    main()

