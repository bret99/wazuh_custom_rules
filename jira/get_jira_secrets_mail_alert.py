import requests
import os
from secret_tokens import secret_tokens, access_token_login, access_token_pass, jira_address

secrets_found_list = []

jira_url = '{}/rest/api/2/search'.format(jira_address)
auth = (access_token_login, access_token_pass)

headers = {'Content-Type': 'application/json'}
params = {
    'jql': 'createdDate>= -1d AND created <= now() ORDER BY updated ASC',
    'fields': '*all',
    'startAt': 0,
    'maxResults': 10000
}

response = requests.get(jira_url, auth=auth, headers=headers, params=params)
jira_data = response.json()

def get_description():
    try:
        item_counter = 0
        while item_counter <= 10001:
            for secret in secret_tokens:
                if secret in str(jira_data["issues"][item_counter]["fields"]["description"]).lower():
                    item = "Secret <" + secret + "> found in description of {0}/browse/{1} => \n".format(jira_address, jira_data["issues"][item_counter]["key"]) + "\n" + str(jira_data["issues"][item_counter]["fields"]["description"]).replace(secret, secret.upper()) + "\nCreated by {0} {1}".format(jira_data["issues"][item_counter]["fields"]["creator"]["name"], jira_data["issues"][item_counter]["fields"]["created"]) + "\n" + "=============================================================================="
                    secrets_found_list.append(item)
            item_counter += 1
    except (IndexError, TypeError):
        pass

def get_comments_body():
    try:
        item_counter = 0
        while item_counter <= 1001:
            for item in jira_data["issues"][item_counter]["fields"]["comment"]["comments"]:
                for secret in secret_tokens:
                    if secret in str(item["body"]).lower():
                        item = "Secret <" + secret + "> found in comments of {0}/browse/{1} => \n".format(jira_address, jira_data["issues"][item_counter]["key"]) + str(item["body"]).replace(secret, secret.upper()) + "\n" + "Created by {0} {1}".format(item["author"]["name"], item["created"]) + "\n" + "=============================================================================="
                        secrets_found_list.append(item)
            item_counter += 1
    except (IndexError, TypeError):
        pass

def get_worklogs_comments():
    try:
        item_counter = 0
        while item_counter <= 1001:
            for item in jira_data["issues"][item_counter]["fields"]["worklog"]["worklogs"]:
                for secret in secret_tokens:
                    if secret in str(item["comment"]).lower():
                        item = "Secret <" + secret + "> found in worklogs comments of {0}/browse/{1} => ".format(jira_address, jira_data["issues"][item_counter]["key"]) + "\n" + str(item["comment"]).replace(secret, secret.upper()) + "\n" + "Created by {0} {1}".format(item["author"]["name"], item["created"]) + "\n" + "=============================================================================="
                        secrets_found_list.append(item)
            item_counter += 1
    except (IndexError, TypeError):
        pass

def write_output():
    with open("{}/jira_secrets_info.txt".format(os.getcwd()), 'w') as output:
        if len(secrets_found_list) == 0:
            output.write("Secrets not found\n")
        output.write("Total amount of found issues is {}\n".format(len(secrets_found_list)))
        for row in secrets_found_list:
            output.write(str(row) + '\n')
        output.write("Total amount of scanned tasks is {}".format(jira_data["total"]))


get_description()
get_comments_body()
get_worklogs_comments()
write_output()
