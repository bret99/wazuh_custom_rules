import requests
import json
import os
from secret_tokens import gitlab_private_token, gitlab_base_url

# Configuration
private_token = gtilab_private_token  # Your GitLab private token
base_url = "{}/api/v4/users?admins=true".format(gitlab_bae_url)
per_page = 100  # Number of results per page
page = 1  # Start from the first page
current_admins = {}
previous_admins_file = 'previous_admins.json'

# Function to fetch GitLab admins
def fetch_admins(page):
    headers = {
        "PRIVATE-TOKEN": private_token
    }
    response = requests.get(f"{base_url}&per_page={per_page}&page={page}", headers=headers)
    return response.json()

# Load previous admin state if exists
def load_previous_admins():
    if os.path.exists(previous_admins_file):
        with open(previous_admins_file, 'r') as file:
            return json.load(file)
    return {}

# Write current admins state to the previous file for future comparisons
def write_current_admins(admins):
    with open(previous_admins_file, 'w') as file:
        json.dump(admins, file)
# Iterate over pages to collect all admins
while True:
    admins = fetch_admins(page)

    if not admins:  # If no more admins are returned, stop the loop
        break

    for admin in admins:
        username = admin['username']
        state = admin['state']
        current_admins[username] = state  # Store username and state

    page += 1  # Move to the next page

# Load previous admins for comparison
previous_admins = load_previous_admins()

# Determine differences
differences = []

# Check for changes in usernames or status
for username, state in current_admins.items():
    if username not in previous_admins:
        differences.append({
            "gitlab_username": username,
            "gitlab_admin_status": state,
            "gitlab_admin_change": "added"
        })
    elif previous_admins[username] != state:
        differences.append({
            "gitlab_username": username,
            "gitlab_admin_status": state,
            "gitlab_admin_change": "status changed"
        })
# Check for removed usernames
for username in previous_admins:
    if username not in current_admins:
        differences.append({
            "gitlab_username": username,
            "gitlab_admin_status": previous_admins[username],
            "gitlab_admin_change": "removed"
        })

# Write differences to output file as separate JSON objects on new lines
if differences:
    with open('differences_admins.json', 'w') as diff_file:
        for diff in differences:
            json.dump(diff, diff_file)
            diff_file.write('\n')  # Write a new line after each JSON object

# Update the previous admins file to store current state
write_current_admins(current_admins)

os.system("rm -f /var/log/gitlab/differences_admins.json")
os.system("cat /usr/local/bin/differences_admins.json > /var/log/gitlab/differences_admins.json")
os.system("rm -f /usr/local/bin/differences_admins.json")
