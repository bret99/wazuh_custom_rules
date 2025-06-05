import json
import os
import requests
from secret_tokens import access_token_login, access_token_pass, confluence_address
from datetime import datetime, timedelta

now = datetime.now()

# Get Confluence tasks for last 6 hours
six_hours_ago = now - timedelta(hours=6)
confluence_url = '{0}/rest/api/content?limit=10000&start=0&postingDay={1}&expand=space,body.storage,version'.format(confluence_addres, six_hours_ago.strftime('%Y-%m-%d'))
auth = (access_token_login, access_token_pass)

headers = {'Content-Type': 'application/json'}
response = requests.get(confluence_url, auth=auth, headers=headers)
confluence_data = response.json()

processed_data = []

for issue in confluence_data["results"]:
    confluence_task = "{}/".format(confluence_address) + issue["_links"].get("webui", "")
    confluence_creator = issue["version"].get("by", {}).get("username", "")
    confluence_creation = issue["version"].get("when", "")
    confluence_space = issue["space"].get("name", "")
    confluence_description = issue["body"].get("storage", "").get("value", "")
    confluence_title = issue["title"]

    event_data = {
        "confluence_task": confluence_task,
        "confluence_creator": confluence_creator,
        "confluence_creation": confluence_creation,
        "confluence_space": confluence_space,
        "confluence_description": confluence_description,
        "confluence_title": confluence_title
    }

    processed_data.append(event_data)

with open('/usr/local/bin/confluence_output_file.json', 'w', encoding='utf-8') as output_file:
    for data in processed_data:
        json.dump(data, output_file, separators=(',', ':'))
        output_file.write('\n')

os.system("cat /usr/local/bin/confluence_output_file.json > /var/log/confluence/tasks.json")
os.system("rm -f /usr/local/bin/confluence_output_file.json")
