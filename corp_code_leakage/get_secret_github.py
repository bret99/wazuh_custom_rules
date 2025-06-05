import aiohttp
import asyncio
import base64
import json
import os
from urllib.parse import quote_plus
from datetime import datetime
from secret_tokens import GITHUB_TOKEN, KEYWORDS

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "PythonScript/1.0"
}

SEARCH_URL = "https://api.github.com/search/code"
RESULT_FILE = "github_search_results.json"

LANGUAGES = ["javascript", "php", "css", "json", "yaml", "xml", "java"] # Substitute for actual ones
RESULTS_PER_PAGE = 100
MAX_PAGES = 5
CONTEXT_LINES = 2
RATE_LIMIT_DELAY = 5

async def fetch(session, url):
    async with session.get(url, headers=HEADERS) as response:
        if response.status == 403 or response.status == 429:
            retry_after = int(response.headers.get("Retry-After", RATE_LIMIT_DELAY))
            print(f"[{datetime.now()}] Limit is up. Waiting for {retry_after} seconds...")
            await asyncio.sleep(retry_after)
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

async def search_code(session, keyword, page):
    query = quote_plus(f"{keyword} in:file language:{LANGUAGES[0]} language:{LANGUAGES[1]}")
    url = f"{SEARCH_URL}?q={query}&per_page={RESULTS_PER_PAGE}&page={page}"
    print(f"[{datetime.now()}] Запрос: {url}")
    result = await fetch(session, url)
    if not result or 'items' not in result:
        return []
    return [
        {
            "keyword": keyword,
            "item": item
        }
        for item in result["items"]
    ]

async def get_file_content(session, item_url):
    result = await fetch(session, item_url)
    if not result or 'content' not in result:
        return None
    try:
        return base64.b64decode(result['content']).decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Decoding error: {e}")
        return None

def find_matches(content, keyword, context_lines=CONTEXT_LINES):
    lines = content.splitlines()
    matches = []
    keyword_lower = keyword.lower()
    for i, line in enumerate(lines):
        if keyword_lower in line.lower():
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            context = "\n".join(lines[start:i]) + \
                      f"\n>>> {line} <<<\n" + \
                      "\n".join(lines[i+1:end])
            matches.append({
                "line_number": i + 1,
                "context": context.strip()
            })
    return matches

async def process_item(session, keyword_item, lock):
    item = keyword_item["item"]
    repo_full_name = item["repository"]["full_name"]
    file_path = item["path"]
    file_html_url = item["html_url"]
    file_api_url = item["url"]

    content = await get_file_content(session, file_api_url)
    if not content:
        return None

    matches = find_matches(content, keyword_item["keyword"])
    if not matches:
        return None

    result = {
        "repo_name": repo_full_name,
        "repo_file_path": file_path,
        "repo_url": file_html_url,
        "repo_keyword": keyword_item["keyword"],
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
                print(f"[Error] File {RESULT_FILE} corrupted. Creating new one.")
                data = []

            data.append(result)

            with open(RESULT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Saved: {repo_full_name}/{file_path}")

        except Exception as e:
            print(f"[Record error] {e}")

    return result

async def run():
    lock = asyncio.Lock()
    async with aiohttp.ClientSession() as session:
        all_items = []
        tasks = []

        for keyword in KEYWORDS:
            for page in range(1, MAX_PAGES + 1):
                tasks.append(search_code(session, keyword, page))

        results = await asyncio.gather(*tasks)
        for page_result in results:
            all_items.extend(page_result)

        print(f"[{datetime.now()}] Files found: {len(all_items)}")

        process_tasks = [process_item(session, item, lock) for item in all_items]
        await asyncio.gather(*process_tasks)

        print(f"[{datetime.now()}] Ready. Results are saved to {RESULT_FILE}")


if __name__ == "__main__":
    test_data = [{"test": "value"}]
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(test_data, f)
    print("Text file created.")

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[INFO] Script stopped by user. Results are already saved.")
