import json
import os
import requests
from secret_tokens import access_token_login, access_token_pass, jira_address

jira_url = '{}/rest/api/2/search'.format(jira_address)
auth = (access_token_login, access_token_pass)

headers = {'Content-Type': 'application/json'}

# Get tasks for last 6 hours
params = {
    'jql': 'createdDate >= -6h AND createdDate <= now() ORDER BY updated ASC',
    'fields': '*all',
    'startAt': 0,
    'maxResults': 10000
}
response = requests.get(jira_url, auth=auth, headers=headers, params=params)
jira_data = response.json()
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

    jira_worklogs_list = issue["fields"].get("worklog", {}).get("worklogs", [])
    jira_worklog = " ".join(worklog["comment"] for worklog in jira_worklogs_list if "comment" in worklog)

    event_data = {
        "jira_task": jira_task,
        "jira_creator": jira_creator,
        "jira_creation": jira_creation,
        "jira_project": jira_project,
        "jira_summary": jira_summary,
        "jira_description": jira_description,
        "jira_comment": jira_comment,
        "jira_worklog": jira_worklog
    }

    processed_data.append(event_data)

with open('/usr/local/bin/jira_output_file.json', 'w', encoding='utf-8') as output_file:
    for data in processed_data:
        json.dump(data, output_file, separators=(',', ':'))
        output_file.write('\n')

os.system("cat /usr/local/bin/jira_output_file.json > /var/log/jira/tasks.json")
os.system("rm -f /usr/local/bin/jira_output_file.json")
