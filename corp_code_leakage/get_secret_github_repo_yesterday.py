import aiohttp
import asyncio
import os
import json
from urllib.parse import quote_plus, urlparse
from datetime import datetime, timedelta
from datetime import datetime, timedelta, timezone
from secret_tokens import GITHUB_TOKEN

# Получаем дату вчерашнего дня в формате YYYY-MM-DD
yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()

# === Настройки ===
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "PythonScript/1.0"
}

SEARCH_URL = "https://api.github.com/search/repositories" 
RESULT_FILE = "yesterday_updated_github_repositories.json"

KEYWORD_IN_NAME = "promed"  # Искать в названиях репозиториев
RESULTS_PER_PAGE = 100      # Максимум разрешено 100
MAX_PAGES = 10              # Всего страниц (до 1000 результатов)

# === Вспомогательные функции ===
async def fetch(session, url):
    async with session.get(url, headers=HEADERS) as response:
        if response.status == 403 or response.status == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"[{datetime.now()}] Лимит превышен. Жду {retry_after} секунд...")
            await asyncio.sleep(retry_after)
            return None
        elif response.status != 200:
            print(f"[{datetime.now()}] Ошибка ({response.status}) при запросе: {url}")
            try:
                text = await response.text()
                print("Тело ответа:", text[:300])
            except:
                pass
            return None
        return await response.json()

def save_results(results):
    try:
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"[{datetime.now()}] Результаты сохранены в {RESULT_FILE}")
    except Exception as e:
        print(f"[Ошибка записи файла] {e}")

# === Парсинг имени пользователя и репозитория из URL ===
def parse_repo_info(repo_url):
    parsed = urlparse(repo_url)
    path = parsed.path.strip("/")
    parts = path.split("/")
    if len(parts) >= 2:
        owner = parts[0]
        repo_name = parts[1]
        return owner, repo_name
    return None, None

# === Главная функция ===
async def run():
    async with aiohttp.ClientSession() as session:
        all_projects = []

        # Получаем дату вчерашнего дня в формате YYYY-MM-DD
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()

        for page in range(1, MAX_PAGES + 1):
            # Добавляем фильтр по дате создания репозитория created:YYYY-MM-DD
            query_date = yesterday.strftime("%Y-%m-%d")
            query = quote_plus(f"{KEYWORD_IN_NAME} in:name created:{query_date}")
            url = f"{SEARCH_URL}?q={query}&per_page={RESULTS_PER_PAGE}&page={page}"
            print(f"[{datetime.now()}] Запрашиваю страницу {page}: {url}")

            result = await fetch(session, url)
            if not result or 'items' not in result:
                break

            for item in result["items"]:
                repo_url = item["html_url"]
                owner, repo_name = parse_repo_info(repo_url)

                # Проверяем точное совпадение ключевого слова в имени
                if KEYWORD_IN_NAME.lower() in item["name"].lower():
                    project = {
                        "repo_name": item["full_name"],
                        "repo_url": repo_url,
                        "repo_owner": owner,
                        "repo_name": repo_name,
                        "repo_star_count": item["stargazers_count"],
                        "repo_description": item["description"] or "",
                        "repo_created_at": item["created_at"]
                    }
                    all_projects.append(project)

            if len(result["items"]) < RESULTS_PER_PAGE:
                break

        print(f"[{datetime.now()}] Найдено репозиториев за {yesterday}: {len(all_projects)}")
        save_results(all_projects)

        print(f"[{datetime.now()}] Готово. Результаты сохранены в {RESULT_FILE}")

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[INFO] Скрипт остановлен пользователем. Результаты уже сохранены.")
