import requests
import json
import os
import shutil
import urllib3
from secret_tokens import vmware_user, vmware_password, vmware_server, vmware_tenant, vmware_vdc_names

# Configuration
user = vmware_user
passw = vmware_password
server = vmware_server
tenant = vmware_tenant
vdc_names = vmware_vdc_names
current_file = "current_vms.json"
previous_file = "previous_vms.json"
differences_file = "differences.json"
auth_string = f"{user}@{tenant}:{passw}"

# Disable the InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_token():
    response = requests.post(
        f"https://{server}/cloudapi/1.0.0/sessions",
        headers={"Accept": "application/*;version=36.2"},
        auth=(user + "@" + tenant, passw),
        verify=False
    )
    return response.headers.get('X-VMWARE-VCLOUD-ACCESS-TOKEN')
  def query_vms(token, vdc_name):
    all_vms = []
    page = 1
    page_size = 25  # Assuming default page size is 25; adjust if necessary.

    while True:
        url = f"https://{server}/api/query?type=vm&fields=name,vdcName,status,ownerName,containerName,networkName,ipAddress,dateCreated"
        filter_string = f"(vdcName=={vdc_name});(isVAppTemplate==false)"

        response = requests.get(url + f"&filter={filter_string}&pageSize={page_size}&page={page}", headers={
            "Accept": "application/*+json;version=36.2",
            "Authorization": f"Bearer {token}"
        }, verify=False)

        vms_data = response.json()
        if 'record' in vms_data and vms_data['record']:
            all_vms.extend(vms_data['record'])
            page += 1  # Go to the next page
        else:
            break  # No more records to process

    return all_vms

def write_to_json(file_path, data):
    with open(file_path, 'w') as json_file:
        for item in data:
            json.dump(item, json_file)
            json_file.write("\n")
def read_previous_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as json_file:
                return [json.loads(line) for line in json_file]
        except json.JSONDecodeError:
            print(f"Error reading {file_path}: The file is empty or corrupted.")
            return []
    return []

def find_power_state_differences(current_data, previous_data):
    differences = []
    previous_dict = {vm['vmName']: vm['powerState'] for vm in previous_data}
    for vm in current_data:
        vm_name = vm['vmName']
        current_power_state = vm['powerState']

        if vm_name in previous_dict:
            previous_power_state = previous_dict[vm_name]
            if current_power_state != previous_power_state:
                differences.append({
                    "vmName": vm_name,
                    "previousPowerState": previous_power_state,
                    "currentPowerState": current_power_state
                })
        else:
            # New VM in current data
            differences.append({
                "vmName": vm_name,
                "previousPowerState": None,
                "currentPowerState": current_power_state
            })

    return differences
  # Get current VMs
token = get_token()
current_vms = []

for vdc in vdc_names:
    vms_data = query_vms(token, vdc)
    for record in vms_data:
        vm_info = {
            "vmName": record.get("name"),
            "powerState": record.get("status"),
            "ipAddress": record.get("ipAddress"),
            "dateCreated": record.get("dateCreated"),
            "containerName": record.get("containerName"),
            "networkName": record.get("networkName"),
            "owner": record.get("ownerName")
        }
        current_vms.append(vm_info)

# Write current VMs to file
write_to_json(current_file, current_vms)

# Read previous VMs
previous_vms = read_previous_data(previous_file)

# Find differences specifically in powerState
differences = find_power_state_differences(current_vms, previous_vms)

# Write differences to file
if differences:
    write_to_json(differences_file, differences)
  # Rename current_vms.json to previous_vms.json for next run comparison
if os.path.exists(previous_file):
    os.remove(previous_file)  # Remove the old previous file if it exists
shutil.move(current_file, previous_file)

os.system("rm -f /var/log/vdc/{}".format(previous_file))
os.system("cat /usr/local/bin/{0} > /var/log/vdc/{1}".format(previous_file, previous_file))
os.system("rm -f /var/log/vdc/{}".format(differences_file))
os.system("cat /usr/local/bin/{0} > /var/log/vdc/{1}".format(differences_file, differences_file))
os.system("rm -f /usr/local/bin/{}".format(differences_file))
