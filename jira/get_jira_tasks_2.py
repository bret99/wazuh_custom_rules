import json
import os
import requests
from secret_tokens import access_token_login, access_token_pass, secret_tokens, jira_address

jira_url = '{}/rest/api/2/search'.format(jira_address)
auth = (access_token_login, access_token_pass)

headers = {'Content-Type': 'application/json'}
params = {
    'jql': 'createdDate >= -6h AND createdDate <= now() ORDER BY updated ASC',
    'fields': '*all',
    'startAt': 0,
    'maxResults': 10000
}
response = requests.get(jira_url, auth=auth, headers=headers, params=params)
jira_data = response.json()

# Prepare a list to store the processed information for each event
processed_data = []

for issue in jira_data["issues"]:
    jira_task = "{}/browse/".format(jira_address) + issue.get("key", "")
    jira_creator = issue["fields"].get("creator", {}).get("name", "")
    jira_creation = issue["fields"].get("created", "")
    jira_project = issue["fields"].get("project", {}).get("key", "")
    jira_summary = issue["fields"].get("summary", "")
    jira_description = issue["fields"].get("description", "")

    jira_comments_list = issue["fields"].get("comment", {}).get("comments", [])
    jira_comment = " ".join(comment["body"] for comment in jira_comments_list)
    jira_comment_creator = " ".join(creator["author"].get("name", "") for creator in jira_comments_list)
    jira_comment_creation = " ".join(creation["created"] for creation in jira_comments_list)

    jira_worklogs_list = issue["fields"].get("worklog", {}).get("worklogs", [])
    jira_worklog = " ".join(worklog["comment"] for worklog in jira_worklogs_list if "comment" in worklog)
    jira_worklog_creator = " ".join(creator["author"].get("name", "") for creator in jira_worklogs_list)
    jira_worklog_creation = " ".join(creation["created"] for creation in jira_worklogs_list)

    for item in secret_tokens:
        if str(item) in str(jira_description).lower():
            event_data = {
            "jira_secret": str(item),
            "jira_secret_site": "description",
            "jira_secret_publisher": jira_creator,
            "jira_secret_creation": jira_creation,
            "jira_task": jira_task,
            "jira_creator": jira_creator,
            "jira_creation": jira_creation,
            "jira_project": jira_project,
            "jira_summary": jira_summary,
            "jira_description": jira_description
            }
            processed_data.append(event_data)
        if str(item) in str(jira_comment).lower():
            event_data = {
            "jira_secret": str(item),
            "jira_secret_site": "comment",
            "jira_secret_publisher": str("[" + jira_comment_creator + "]"),
            "jira_secret_creation": str("[" + jira_comment_creation + "]"),
            "jira_task": jira_task,
            "jira_creator": jira_creator,
            "jira_creation": jira_creation,
            "jira_project": jira_project,
            "jira_summary": jira_summary,
            "jira_comment": str("[" + jira_comment + "]")
            }
            processed_data.append(event_data)
        if str(item) in str(jira_worklog).lower():
            event_data = {
            "jira_secret": str(item),
            "jira_secret_site": "worklog",
            "jira_secret_publisher": str("[" + jira_worklog_creator + "]"),
            "jira_secret_creation":str("[" + jira_worklog_creation + "]"),
            "jira_task": jira_task,
            "jira_creator": jira_creator,
            "jira_creation": jira_creation,
            "jira_project": jira_project,
            "jira_summary": jira_summary,
            "jira_worklog": str("[" + jira_worklog + "]")
            }
            processed_data.append(event_data)
        else:
            event_data = {
            "jira_secret": "null",
            "jira_secret_site": "null",
            "jira_task": jira_task,
            "jira_creator": jira_creator,
            "jira_creation": jira_creation,
            "jira_project": jira_project,
            "jira_summary": jira_summary
            }
            processed_data.append(event_data)


with open('/usr/local/bin/jira_output_file.json', 'w', encoding='utf-8') as output_file:
    for data in processed_data:
        json.dump(data, output_file, separators=(',', ':'))
        output_file.write('\n')

os.system("cat /usr/local/bin/jira_output_file.json | sort -u > /var/log/jira/tasks.json")
os.system("rm -f /usr/local/bin/jira_output_file.json")
