#!/usr/bin/env python
# -*- coding: utf-8 -*-
from opensearchpy import OpenSearch
from datetime import datetime, timedelta
import requests
import json
from secret_tokens import HOST, INDEX, OS_USERNAME, OS_PASSWORD, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SENDER, DOMAIN, VK_TEAMS_TOKEN, VK_TEAMS_CHAT_ID, VK_TEAMS_HOOK_URL 

def get_opensearch_client():
    return OpenSearch(
        hosts=[HOST],
        http_auth=(OS_USERNAME, OS_PASSWORD),
        use_ssl=True,
        verify_certs=False
    )

def get_risk_level_and_emoji(level):
    """Function to determine risk level and emoji"""
    if level == 11:
        return "moderate", "✅"  # Green checkmark
    elif level == 12:
        return "high", "🔥"  # Fire
    elif level >= 13:
        return "critical", "❌"  # Red cross
    else:
        return "unknown", "❓"  # Question mark

def send_to_vk_teams(message):
    """Send message to VK Teams"""
    data = {
        "token": VK_TEAMS_TOKEN,
        "chatId": VK_TEAMS_CHAT_ID,
        "text": message
    }
    
    headers = {"content-type": "application/json", "Accept-Charset": "UTF-8"}
    try:
        response = requests.post(url=VK_TEAMS_HOOK_URL, headers=headers, params=data, verify=False)
        response.raise_for_status()
        print(f"Message sent to VK Teams")
    except Exception as e:
        print(f"Error sending to VK Teams: {e}")

def fetch_alerts(client):
    """Search for events with level 11 and higher for the last 5 minutes"""
    query = {
        "size": 1000,
        "sort": [{"@timestamp": {"order": "desc"}}],
        "query": {
            "bool": {
                "must": [
                    {"range": {"rule.level": {"gte": 11}}}, # Change rule level if necessary
                    {"range": {"@timestamp": {"gte": "now-3m/m", "lt": "now"}}} # Change time period if necessary
                ]
            }
        }
    }

    resp = client.search(index=INDEX, body=query)
    total = resp.get('hits', {}).get('total', {}).get('value', 0)
    if total == 0:
        print("No events with level 11+ found for the last 5 minutes.")
        return []

    return resp.get('hits', {}).get('hits', [])

def format_alert_message(alert):
    """Format alert message in VK Teams style"""
    alert_data = alert["_source"]
    
    # Get risk level and emoji
    alert_level = alert_data.get("rule", {}).get("level", "N/A")
    risk_level_text, risk_level_emoji = get_risk_level_and_emoji(int(alert_level))
    
    # Main fields
    description = alert_data.get("rule", {}).get("description", "N/A")
    agent_hostname = alert_data.get("agent", {}).get("name", "N/A")
    timestamp = alert_data.get("@timestamp", "N/A")
    
    # Additional fields (if available)
    rule_id = alert_data.get("rule", {}).get("id", "N/A")
    rule_groups = alert_data.get("rule", {}).get("groups", [])
    
    # Format message
    message = f"🚨 New security event\n\n"
    message += f"🔒 Risk level: {risk_level_text} {risk_level_emoji}\n"
    message += f"📊 Alert level: {alert_level}\n"
    message += f"📌 Description: {description}\n"
    message += f"👤 Source: {agent_hostname}\n"
    message += f"🆔 Rule ID: {rule_id}\n"
    message += f"⏰ Time: {timestamp}\n"
    
    if rule_groups:
        message += f"🏷️ Groups: {', '.join(rule_groups)}\n"
    
    # Add MITRE information if available
    mitre_info = alert_data.get("rule", {}).get("mitre", {})
    if mitre_info:
        tactics = mitre_info.get("tactic", [])
        techniques = mitre_info.get("technique", [])
        
        if tactics:
            message += f"🎯 MITRE Tactics: {', '.join(tactics)}\n"
        if techniques:
            message += f"🎯 MITRE Techniques: {', '.join(techniques)}\n"
    
    return message

def main():
    """Main function"""
    client = get_opensearch_client()
    alerts = fetch_alerts(client)
    
    if not alerts:
        print("No events to send.")
        return
    
    print(f"Found {len(alerts)} events with level 11+ for the last 5 minutes")
    
    for alert in alerts:
        try:
            message = format_alert_message(alert)
            send_to_vk_teams(message)
            print(f"Sent event level {alert['_source'].get('rule', {}).get('level', 'N/A')}")
        except Exception as e:
            print(f"Error processing event: {e}")

if __name__ == "__main__":
    main()
