import requests
import json
import os
from secret_tokens import gitlab_private_token, gtilab_base_url

# Configuration
private_token = gitlab_private_token  # Your GitLab private token
base_url = "{}/api/v4/runners/all".fromat(gtilab_base_url)
per_page = 100  # Number of results per page
page = 1  # Start from the first page
results = []

# Function to fetch GitLab runners
def fetch_runners(page):
    headers = {
        "PRIVATE-TOKEN": private_token
    }
    response = requests.get(f"{base_url}?per_page={per_page}&page={page}", headers=headers)
    return response.json()

# Iterate over pages
while True:
    runners = fetch_runners(page)

    if not runners:  # If no more runners are returned, stop the loop
        break

    results.extend(runners)  # Collect results from the current page
    page += 1  # Move to the next page

# Write results to a JSON file with each entry being a separate line
with open('runners.json', 'w') as outfile:
    for runner in results:
        json.dump(runner, outfile)
        outfile.write('\n')  # Write a new line after each entry
os.system("rm -f /var/log/gitlab/runners.json")
os.system("cat /usr/local/bin/runners.json > /var/log/gitlab/runners.json")
os.system("rm -f /usr/local/bin/runners.json")
