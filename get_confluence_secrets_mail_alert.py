import requests
import os
from datetime import date, timedelta
from secret_tokens import secret_tokens, access_token_login, access_token_pass, confluence_address

secrets_found_list = []

posting_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
confluence_url = '{0}/rest/api/content?limit=10000&start=0&postingDay={1}&expand=space,body.storage,version'.format(confluence_address, posting_date)
auth = (access_token_login, access_token_pass)

headers = {'Content-Type': 'application/json'}
response = requests.get(confluence_url, auth=auth, headers=headers)
confluence_data = response.json()

def get_issue_body():
    try:
        item_counter = 0
        while item_counter < confluence_data["size"]:
            for secret in secret_tokens:
                if secret in str(confluence_data["results"][item_counter]["body"]["storage"]["value"]).lower():
                    item = "Secret <" + secret + "> found in description of {0}/{1} => \n".format(confluence_address, confluence_data["results"][item_counter]["_links"]["webui"]) + "\n" + "\nCreated by {0} {1}".format(confluence_data["results"][item_counter]["version"]["by"]["username"], confluence_data["results"][item_counter]["version"]["when"]) + "\n" + "=============================================================================="
                    secrets_found_list.append(item)
            item_counter += 1
    except (IndexError, TypeError):
        pass

def get_issue_title():
    try:
        item_counter = 0
        while item_counter < confluence_data["size"]:
            for secret in secret_tokens:
                if secret in str(confluence_data["results"][item_counter]["title"]).lower():
                    item = "Secret <" + secret + "> found in title of {0}/{1} => \n".format(confluence_address, confluence_data["results"][item_counter]["_links"]["webui"]) + "\n" + str(confluence_data["results"][item_counter]["title"]).replace(secret, secret.upper()) + "\nCreated by {0} {1}".format(confluence_data["results"][item_counter]["version"]["by"]["username"], confluence_data["results"][item_counter]["version"]["when"]) + "\n" + "=============================================================================="
                    secrets_found_list.append(item)
            item_counter += 1
    except (IndexError, TypeError):
        pass

def write_output():
    with open("{}/confluence_secrets_info.txt".format(os.getcwd()), 'w') as output:
        if len(secrets_found_list) == 0:
            output.write("Secrets not found\n")
        output.write("Total amount of found issues is {}\n".format(len(secrets_found_list)))
        for row in secrets_found_list:
            output.write(str(row) + '\n')
        output.write("Total amount of tasks is {}".format(confluence_data["size"]))


get_issue_title()
get_issue_body()
write_output()
