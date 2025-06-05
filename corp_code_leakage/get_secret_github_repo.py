import aiohttp
import asyncio
import os
import json
from urllib.parse import quote_plus
from datetime import datetime
from secret_tokens import GITHUB_TOKEN, KEYWORD_IN_NAME

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "PythonScript/1.0"
}

SEARCH_URL = "https://api.github.com/search/repositories"
RESULT_FILE = "github_secret_repos.json"

MAX_PAGES = 5
RESULTS_PER_PAGE = 100

async def fetch(session, url):
    async with session.get(url, headers=HEADERS) as response:
        if response.status == 403 or response.status == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"[{datetime.now()}] Limit is up. Waiting for {retry_after} seconds...")
            await asyncio.sleep(retry_after)
            return None
        elif response.status != 200:
            print(f"[{datetime.now()}] Error ({response.status}) from request: {url}")
            try:
                text = await response.text()
                print("Response body:", text[:300])
            except:
                pass
            return None
        return await response.json()

def save_results(results):
    try:
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"[{datetime.now()}] Results are saved to {RESULT_FILE}")
    except Exception as e:
        print(f"[File record error] {e}")

async def run():
    async with aiohttp.ClientSession() as session:
        all_projects = []

        for page in range(1, MAX_PAGES + 1):
            query = quote_plus(f"{KEYWORD_IN_NAME} in:name")
            url = f"{SEARCH_URL}?q={query}&per_page={RESULTS_PER_PAGE}&page={page}"
            print(f"[{datetime.now()}] Requesting page {page}: {url}")

            result = await fetch(session, url)
            if not result or 'items' not in result:
                break

            filtered = [
                {
                    "repo_name": item["full_name"],
                    "repo_url": item["html_url"],
                    "repo_star_count": item["stargazers_count"]
                }
                for item in result["items"]
                if KEYWORD_IN_NAME.lower() in item["name"].lower()
            ]

            all_projects.extend(filtered)

            if len(result["items"]) < RESULTS_PER_PAGE:
                break

        print(f"[{datetime.now()}] Found repositories with '{KEYWORD_IN_NAME}' in name: {len(all_projects)}")
        save_results(all_projects)

        print(f"[{datetime.now()}] Ready. Report file is {RESULT_FILE}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[INFO] Script stopped by user. Results are already saved.")
