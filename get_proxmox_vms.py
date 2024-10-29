import requests
import json
import argparse
from datetime import datetime
import os
from secret_tokens import PM_node, PM_cluster, PM_username, PM_password

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Proxmox VM Information Retriever")
parser.add_argument("--node", default=PM_node, help="Proxmox node name (default: {})".format(PM_node))
parser.add_argument("--cluster", default=PM_cluster, help="Proxmox cluster name (default: {})".format(PM_cluster))
parser.add_argument("--output-file", default="vm_info.json", help="Output file name (default: vm_info.json)")
parser.add_argument("--differences-file", default="vm_differences.json", help="Differences file name (default: vm_differences.json)")
parser.add_argument("--status", help="Filter VMs by status (e.g., 'running', 'stopped')")
args = parser.parse_args()
report_dir = "/var/log/proxmox"

# Proxmox API credentials
proxmox_host = f"https://{args.cluster}:8006"
proxmox_username = PM_username
proxmox_password = PM_password

# URL for the Proxmox API endpoint to get the list of VMs
qemu_api_url = f"{proxmox_host}/api2/json/nodes/{args.node}/qemu"
lxc_api_url = f"{proxmox_host}/api2/json/nodes/{args.node}/lxc"

# Authenticate with Proxmox
auth_data = {
    "username": proxmox_username,
    "password": proxmox_password
}

auth_response = requests.post(f"{proxmox_host}/api2/json/access/ticket", data=auth_data)
if auth_response.status_code == 200:
    csrf_token = auth_response.json()["data"]["CSRFPreventionToken"]
    session_ticket = auth_response.json()["data"]["ticket"]
else:
    print(f"Error authenticating with Proxmox: {auth_response.status_code} - {auth_response.text}")
    exit(1)

# Set the headers for the API requests
headers = {
    "CSRFPreventionToken": csrf_token,
    "Cookie": f"PVEAuthCookie={session_ticket}"
}

# Get the list of QEMU VMs
qemu_response = requests.get(qemu_api_url, headers=headers)
if qemu_response.status_code == 200:
    qemu_vm_data = qemu_response.json().get("data", [])
else:
    print(f"Error retrieving QEMU VM data: {qemu_response.status_code} - {qemu_response.text}")
    qemu_vm_data = []

# Get the list of LXC VMs
lxc_response = requests.get(lxc_api_url, headers=headers)
if lxc_response.status_code == 200:
    lxc_vm_data = lxc_response.json().get("data", [])
else:
    print(f"Error retrieving LXC VM data: {lxc_response.status_code} - {lxc_response.text}")
    lxc_vm_data = []
# Filter VMs by status if specified
if args.status:
    qemu_vm_data = [vm for vm in qemu_vm_data if vm["status"] == args.status]
    lxc_vm_data = [vm for vm in lxc_vm_data if vm["status"] == args.status]

# Collect VM information
all_vm_data = []
for vm in qemu_vm_data:
    vm_info = {
        "vm_ID": str(vm["vmid"]),
        "vm_name": vm["name"],
        "vm_status": vm["status"],
        "vm_type": "qemu"
    }
    all_vm_data.append(vm_info)

for vm in lxc_vm_data:
    vm_info = {
        "vm_ID": str(vm["vmid"]),
        "vm_name": vm["name"],
        "vm_status": vm["status"],
        "vm_type": "lxc"
    }
    all_vm_data.append(vm_info)

# Write the VM information to a JSON file
with open(args.output_file, "w") as f:
    for vm in all_vm_data:
        json.dump(vm, f)
        f.write("\n")

# Load the previous VM information from the output file
try:
    with open(args.output_file, "r") as f:
        previous_vm_data = [json.loads(line) for line in f]
except FileNotFoundError:
    previous_vm_data = []


# Find the differences between the current and previous VM data
differences = []
for current_vm in all_vm_data:
    found = False
    for previous_vm in previous_vm_data:
        if current_vm["vm_ID"] == previous_vm["vm_ID"]:
            found = True
            if current_vm["vm_status"] != previous_vm["vm_status"]:
                differences.append({
                    "timestamp": datetime.now().isoformat(),
                    "current": current_vm,
                    "previous": previous_vm
                })
            break
    if not found:
        differences.append({
            "timestamp": datetime.now().isoformat(),
            "current": current_vm,
            "previous": None
        })

# Write the differences to a JSON file
with open(args.differences_file, "w") as f:
    for diff in differences:
        json.dump(diff, f)
        f.write("\n")


# Delete previous report
os.system("rm -f {0}/{1}".format(report_dir, args.output_file))
os.system("rm -f {0}/{1}".format(report_dir, args.differences_file))

# Write current report
os.system("cat {0} > {1}/{2}".format(args.differences_file, report_dir, args.differences_file))
os.system("cat {0} > {1}/{2}".format(args.output_file, report_dir, args.output_file))
