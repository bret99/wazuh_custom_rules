#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import requests
import datetime

token = "" # Insert here bot token
chat_id = "" # Insert here channel ID
alert_file = open(sys.argv[1])
alert_json = json.loads(alert_file.read())
alert_file.close()
#date = datetime.datetime.now()
alert_level = alert_json["rule"]["level"] if "level" in alert_json["rule"] else "N/A"

# Function to map alert level to risk level and emoji
def get_risk_level_and_emoji(level):
    if level == 11:
        return "moderate", "✅"
    elif level == 12:
        return "high", "🔥"
    elif level >= 13:
        return "critical", "❌"
    
# Map alert level to risk level and emoji
risk_level_text, risk_level_emoji = get_risk_level_and_emoji(int(alert_level))
description = alert_json["rule"]["description"] if "description" in alert_json["rule"] else "N/A"
agent_hostname = alert_json["agent"]["name"] if "name" in alert_json["agent"] else "N/A"

#agent_ip = alert_json["agent"]["ip"] if "ip" in alert_json["agent"] else "N/A"
#ip = alert_json["data"]["srcip"] if "srcip" in alert_json["data"] else "N/A"
#status_code = alert_json["data"]["id"] if "id" in alert_json["data"] else "N/A"
#geo = alert_json["GeoLocation"]["country_name"] if "GeoLocation" in alert_json else "N/A"
#full_log = alert_json["full_log"] if "full_log" in alert_json else "N/A"
#technique = alert_json["rule"]["mitre"]["technique"] if "mitre" in alert_json["rule"] else "N/A"
#tactic = alert_json["rule"]["mitre"]["tactic"] if "mitre" in alert_json["rule"] else "N/A"

hook_url = "https://myteam.mail.ru/bot/v1/messages/sendText"
text = f"🔒Risk level: {risk_level_text} {risk_level_emoji} \n📌Description: {description} \n👤Source: {agent_hostname}"
data = {
    "token": token,
    "chatId": chat_id,
    "text": str(text)
}

headers = {"content-type": "application/json", "Accept-Charset": "UTF-8"}
requests.post(url=hook_url, headers=headers, params=data, verify=False)

sys.exit(0)
