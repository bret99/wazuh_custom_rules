import aiohttp
import asyncio
import os
from urllib.parse import quote_plus
from datetime import datetime
import json
from secret_tokens import GITLAB_TOKEN, KEYWORD_IN_NAME

GITLAB_INSTANCE = "https://gitlab.com"

SEARCH_PROJECTS_URL = f"{GITLAB_INSTANCE}/api/v4/projects"
RESULT_FILE = "gitlab_secret_repos.json"


HEADERS = {
    "PRIVATE-TOKEN": GITLAB_TOKEN,
    "User-Agent": "PythonScript/1.0"
}

async def fetch(session, url):
    async with session.get(url, headers=HEADERS) as response:
        if response.status == 403 or response.status == 429:
            print(f"[{datetime.now()}] Limit is up.")
            return None
        elif response.status != 200:
            print(f"[{datetime.now()}] Error ({response.status}) at request: {url}")
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
        page = 1
        per_page = 20

        while True:
            encoded_keyword = quote_plus(KEYWORD_IN_NAME)
            url = f"{SEARCH_PROJECTS_URL}?search={encoded_keyword}&search_names_and_desc=true&per_page={per_page}&page={page}"
            print(f"[{datetime.now()}] Requesting page {page}: {url}")
            projects = await fetch(session, url)

            if not projects:
                break

            filtered = [
                {
                    "repo_name": p["name"],
                    "repo_url": p["web_url"],
                    "repo_namespace": p["namespace"]["name"] if "namespace" in p else ""
                }
                for p in projects
                if KEYWORD_IN_NAME.lower() in p["name"].lower()
            ]

            all_projects.extend(filtered)

            if len(projects) < per_page:
                break
            page += 1

        print(f"[{datetime.now()}] Found projects with '{KEYWORD_IN_NAME}' in name: {len(all_projects)}")
        save_results(all_projects)

        print(f"[{datetime.now()}] Ready. Results are saved to {RESULT_FILE}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[INFO] Script stopped by user. Results are already saved.")
