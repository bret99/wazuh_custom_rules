import requests
import json
import warnings
import os
form secret_tokens import wazuh_manager

# URL for the Wazuh authentication endpoint
url = "{}/security/user/authenticate".format(wazuh_manager)

# Wazuh credentials
username = "wazuh-wui"
password = "" # insert here password for wazuh-wui 

# Disable the InsecureRequestWarning
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Make the authentication request
response = requests.post(url, auth=(username, password), verify=False)

# Check the response status code
if response.status_code == 200:
    wazuh_token = response.json()["data"]["token"]
else:
    print(f"Authentication failed with status code: {response.status_code}")


# 2. Get a list of active Wazuh agents
agents_url = "{}/agents?status=active".format(wazuh_manager)
agents_headers = {"Authorization": f"Bearer {wazuh_token}"}
agents_response = requests.get(agents_url, headers=agents_headers, verify=False)
agents_response.raise_for_status()
agent_info = {agent["id"]: {"ip": agent["ip"], "name": agent["name"], "os": agent["os"]["name"], "version": agent["os"]["version"]} for agent in agents_response.json()["data"]["affected_items"]}

# 3. Get a list of processes for every Wazuh agent
agent_processes = {}
for agent_id, agent_data in agent_info.items():
    processes_url = f"{wazuh_manager}/syscollector/{agent_id}/processes"
    processes_headers = {"Authorization": f"Bearer {wazuh_token}"}
    processes_response = requests.get(processes_url, headers=processes_headers, verify=False)
    processes_response.raise_for_status()
    agent_processes[agent_id] = [proc["name"] for proc in processes_response.json()["data"]["affected_items"]]

# 4. Convert text file to python list
with open("processes.txt", "r") as f:
    processes_to_search = [line.strip() for line in f]

# 5. Search for processes in Wazuh agents and write to JSON file
output = []
for process in processes_to_search:
    for agent_id, agent_procs in agent_processes.items():
        if process in agent_procs:
            output.append({"agent_id": agent_id, "agent_ip": agent_info[agent_id]["ip"], "agent_name": agent_info[agent_id]["name"], "agent_os": agent_info[agent_id]["os"], "agent_os_version": agent_info[agent_id]["version"], "process_found": process})

with open("wazuh_process_search.json", "w", encoding='utf-8') as f:
    try:
        for result in output:
            f.write(json.dumps(result, separators=(',', ':')))
            f.write("\n")
    except TypeError:
        pass
os.system("rm -f /var/log/wazuh/processes.json")
os.system("cat wazuh_process_search.json > /var/log/wazuh/processes.json")
os.system("rm -f wazuh_process_search.json")
