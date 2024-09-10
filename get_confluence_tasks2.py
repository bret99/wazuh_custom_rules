import json
import os
import requests
from secret_tokens import access_token_login, access_token_pass, secret_tokens
from datetime import datetime, timedelta

now = datetime.now()
six_hours_ago = now - timedelta(hours=6)
confluence_url = 'https://confluence.is-mis.ru/rest/api/content?limit=10000&start=0&postingDay={}&expand=space,body.storage,version'.format(six_hours_ago.strftime('%Y-%m-%d'))
auth = (access_token_login, access_token_pass)

headers = {'Content-Type': 'application/json'}
response = requests.get(confluence_url, auth=auth, headers=headers)
confluence_data = response.json()

# Prepare a list to store the processed information for each event
processed_data = []

for issue in confluence_data["results"]:
    confluence_task = "https://confluence.is-mis.ru/" + issue["_links"].get("webui", "")
    confluence_creator = issue["version"].get("by", {}).get("username", "")
    confluence_creation = issue["version"].get("when", "")
    confluence_space = issue["space"].get("name", "")
    confluence_description = issue["body"].get("storage", "").get("value", "")
    confluence_title = issue["title"]

    for item in secret_tokens:
        if str(item) in str(confluence_description).lower():
            event_data = {
            "confluence_secret": str(item),
            "confluence_secret_site": "description",
            "confluence_task": confluence_task,
            "confluence_creator": confluence_creator,
            "confluence_creation": confluence_creation,
            "confluence_space": confluence_space,
            "confluence_description": confluence_description,
            "confluence_title": confluence_title
            }
            processed_data.append(event_data)
        elif str(item) in str(confluence_title).lower():
            event_data = {
            "confluence_secret": str(item),
            "confluence_secret_site": "title",
            "confluence_task": confluence_task,
            "confluence_creator": confluence_creator,
            "confluence_creation": confluence_creation,
            "confluence_space": confluence_space,
            "confluence_title": confluence_title
            }
            processed_data.append(event_data)
        else:
            event_data = {
            "confluence_secret": "null",
            "confluence_secret_site": "null",
            "confluence_task": confluence_task,
            "confluence_creator": confluence_creator,
            "confluence_creation": confluence_creation,
            "confluence_space": confluence_space,
            "confluence_title": confluence_title
            }
            processed_data.append(event_data)


with open('confluence_output_file.json', 'w', encoding='utf-8') as output_file:
    for data in processed_data:
        json.dump(data, output_file, separators=(',', ':'))
        output_file.write('\n')

os.system("cat confluence_output_file.json | sort -u > /var/log/confluence/tasks.json")
os.system("rm -f /usr/local/bin/confluence_output_file.json")
