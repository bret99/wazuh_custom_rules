import aiohttp
import asyncio
import os
import json
from urllib.parse import quote_plus
from datetime import datetime, timedelta, timezone
from secret_tokens import GITLAB_TOKEN, KEYWORD_IN_NAME

GITLAB_INSTANCE = "https://gitlab.com" 

SEARCH_PROJECTS_URL = f"{GITLAB_INSTANCE}/api/v4/projects"
RESULT_FILE = "yesterday_updated_gitlab_repositories.json"

TARGET_FILES = ["README.md", "readme.md"]  # Files to find in
MAX_PAGES = 10
PER_PAGE = 20

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
        print(f"[{datetime.now()}] Results are saved at {RESULT_FILE}")
    except Exception as e:
        print(f"[File record error] {e}")

def parse_project_info(project_url):
    from urllib.parse import urlparse
    parsed = urlparse(project_url)
    path = parsed.path.strip("/")
    parts = path.split("/")
    if len(parts) >= 2:
        owner = parts[0]
        project_name = parts[1]
        return owner, project_name
    return None, None


async def run():
    async with aiohttp.ClientSession() as session:
        all_projects = []

        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()

        for page in range(1, MAX_PAGES + 1):
            encoded_keyword = quote_plus(KEYWORD_IN_NAME)
            url = (
                f"{SEARCH_PROJECTS_URL}?search={encoded_keyword}"
                f"&created_after={yesterday}T00:00:00Z"
                f"&page={page}&per_page={PER_PAGE}"
            )
            print(f"[{datetime.now()}] Requesting page {page}: {url}")

            projects = await fetch(session, url)
            if not projects:
                break

            for p in projects:
                created_at_str = p["created_at"]
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    project_date = created_at.date()

                    if project_date >= yesterday:
                        if KEYWORD_IN_NAME.lower() in p["name"].lower():
                            filtered_project = {
                                "repo_name": p["name"],
                                "repo_url": p["web_url"],
                                "repo_owner": p["namespace"]["path"] if "namespace" in p else "",
                                "repo_created_at": created_at_str
                            }
                            all_projects.append(filtered_project)
                    else:
                        continue

                except Exception as e:
                    print(f"[Date parsing error] {p['name']}: {e}")
                    continue

            if len(projects) < PER_PAGE:
                break

        print(f"[{datetime.now()}] Found projects for {yesterday}: {len(all_projects)}")
        save_results(all_projects)

        print(f"[{datetime.now()}] Ready. Results are saved at {RESULT_FILE}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[INFO] Script stopped by user. Results are already saved.")
