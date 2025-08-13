#!/bin/bash

# Reports files
current_file="/var/log/current_vms.json"
previous_file="/var/log/previous_vms.json"
diff_file="/var/log/differences_vms.json"
rm -f "$diff_file"

# Getting VMs IP
get_vm_ip() {
    local vmid="$1"
    local ip=""

    if qm guest cmd "$vmid" network-get-interfaces &>/dev/null; then
        ip=$(qm guest cmd "$vmid" network-get-interfaces 2>/dev/null | \
             jq -r '.[] | select(.name != "lo") | .["ip-addresses"]?[] | select(.["ip-address-type"] == "ipv4") | .["ip-address"]' | \
             head -n 1)
    fi

    if [[ -z "$ip" ]]; then
        local mac=$(qm config "$vmid" | grep -oP 'net\d+:.*,mac=\K[^,]+' 2>/dev/null | head -n 1)
        if [[ -n "$mac" ]]; then
            ip=$(arp -n | grep -i "$mac" | grep -oP '^\S+' | head -n 1)
        fi
    fi

    echo "${ip:-null}"
}

# 1. Writing current VMs conditions at current_vms.json
> "$current_file"
qm list --full | tail -n +2 | while read -r line; do
    vmid=$(echo "$line" | awk '{print $1}')
    name=$(echo "$line" | awk '{print $2}')
    status=$(echo "$line" | awk '{print $3}' | tr '[:upper:]' '[:lower:]')
    ram=$(echo "$line" | awk '{print $4}')
    disk=$(echo "$line" | awk '{print $5}')
    ip=$(get_vm_ip "$vmid")

    jq -c -n \
        --arg vm_name "$name" \
        --arg vm_status "$status" \
        --arg vm_ram "$ram" \
        --arg vm_disk "$disk" \
        --arg vm_ip "$ip" \
        '{
            "proxmox.vm_name": $vm_name,
            "proxmox.vm_status": $vm_status,
            "proxmox.vm_ram": $vm_ram,
            "proxmox.vm_disk": $vm_disk,
            "proxmox.vm_ip": $vm_ip
        }' >> "$current_file"
done
# 2. Compare to previuos VMs condition report (if target file exists)
> "$diff_file"
if [[ -f "$previous_file" ]]; then
    while IFS= read -r current_line; do
        vm_name=$(echo "$current_line" | jq -r '.["proxmox.vm_name"]')
        current_status=$(echo "$current_line" | jq -r '.["proxmox.vm_status"]')
        
        previous_line=$(grep -F "\"proxmox.vm_name\":\"$vm_name\"" "$previous_file" | head -n 1)
        if [[ -n "$previous_line" ]]; then
            previous_status=$(echo "$previous_line" | jq -r '.["proxmox.vm_status"]')

            if [[ "$current_status" != "$previous_status" ]]; then
                jq -c -n \
                    --arg vm_name "$vm_name" \
                    --arg vm_status_prev "$previous_status" \
                    --arg vm_status_curr "$current_status" \
                    --arg vm_ram "$(echo "$current_line" | jq -r '.["proxmox.vm_ram"]')" \
                    --arg vm_disk "$(echo "$current_line" | jq -r '.["proxmox.vm_disk"]')" \
                    --arg vm_ip "$(echo "$current_line" | jq -r '.["proxmox.vm_ip"]')" \
                    '{
                        "proxmox.vm_name": $vm_name,
                        "proxmox.vm_status_prev": $vm_status_prev,
                        "proxmox.vm_status_curr": $vm_status_curr,
                        "proxmox.vm_ram": $vm_ram,
                        "proxmox.vm_disk": $vm_disk,
                        "proxmox.vm_ip": $vm_ip
                    }' >> "$diff_file"
            fi
        fi
    done < "$current_file"
fi

# 3. Updating previous_vms.json
rm -f "$previous_file"
cat "$current_file" > "$previous_file"
rm -f "$current_file"
