import aiohttp
import asyncio
import os
import base64
from urllib.parse import quote_plus
from datetime import datetime
from secret_tokens import GITLAB_TOKEN, KEYWORDS

GITLAB_INSTANCE = "https://gitlab.com" 

SEARCH_PROJECTS_URL = f"{GITLAB_INSTANCE}/api/v4/projects"
GET_FILE_URL_TEMPLATE = f"{GITLAB_INSTANCE}/api/v4/projects/{{project_id}}/repository/files/{{file_path}}?ref={{branch}}"

RESULT_FILE = "gitlab_search_results.json"

TARGET_FILES = ["README.md", "readme.md", "index.php", "main.js"]
CONTEXT_LINES = 2

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
            return None
        return await response.json()

async def get_file_content(session, project_id, file_path="README.md", branch="main"):
    encoded_path = quote_plus(file_path)
    url = GET_FILE_URL_TEMPLATE.format(project_id=project_id, file_path=encoded_path, branch=branch)
    result = await fetch(session, url)

    if not result or 'content' not in result:
        return None

    try:
        return base64.b64decode(result['content']).decode('utf-8', errors='replace')
    except Exception as e:
        print(f"File decoding error {file_path}: {e}")
        return None

def find_matches(content, keywords, context_lines=CONTEXT_LINES):
    lines = content.splitlines()
    matches = []
    for keyword in keywords:
        keyword_lower = keyword.lower()
        for i, line in enumerate(lines):
            if keyword_lower in line.lower():
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                context = "\n".join(lines[start:i]) + \
                          f"\n>>> {line} <<<\n" + \
                          "\n".join(lines[i+1:end])
                matches.append({
                    "keyword": keyword,
                    "line_number": i + 1,
                    "context": context.strip()
                })
    return matches

async def process_project(session, project, lock):
    project_id = project["id"]
    project_name = project["name"]
    project_url = project["web_url"]

    print(f"[{datetime.now()}] Checking project: {project_name}")

    branches = [project.get("default_branch"), "main", "master"]
    content = None
    for branch in branches:
        if branch:
            for file_path in TARGET_FILES:
                content = await get_file_content(session, project_id, file_path, branch)
                if content:
                    break
            if content:
                break

    if not content:
        return None

    matches = find_matches(content, KEYWORDS)
    if not matches:
        return None

    result = {
        "repo_name": project_name,
        "repo_url": project_url,
        "repo_matches": matches
    }

    async with lock:
        try:
            try:
                if os.path.exists(RESULT_FILE):
                    with open(RESULT_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    data = []
            except json.JSONDecodeError:
                data = []

            data.append(result)

            with open(RESULT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Saved: {project_name}")
        except Exception as e:
            print(f"[Record error] {e}")

    return result

async def run():
    lock = asyncio.Lock()
    async with aiohttp.ClientSession() as session:
        all_projects = []
        per_page = 20

        for keyword in KEYWORDS:
            page = 1
            while True:
                encoded_keyword = quote_plus(keyword.strip())
                url = f"{GITLAB_INSTANCE}/api/v4/projects?search={encoded_keyword}&per_page={per_page}&page={page}"
                print(f"[{datetime.now()}] Requesting page {page} for '{keyword}': {url}")
                
                projects = await fetch(session, url)
                if not projects:
                    break

                new_projects = [
                    p for p in projects 
                    if p not in all_projects  # Проверяем дубликаты по ID
                ]
                all_projects.extend(new_projects)

                if len(projects) < per_page:
                    break
                page += 1

        print(f"[{datetime.now()}] Found projects: {len(all_projects)}")

        tasks = [process_project(session, project, lock) for project in all_projects]
        await asyncio.gather(*tasks)

        print(f"[{datetime.now()}] Ready.Results saved to RESULT_FILE}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[INFO] Script stopped by user. Results are already saved.")
