# -*- coding: utf-8 -*-
"""
VK Teams Notification Module
Handles message sending to VK Teams via Webhooks.
Dependencies: access_tokens.py, requests, urllib3
"""

import requests
import urllib3

# SSL warnings hard supresiion
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from access_tokens import VK_TEAMS_TOKEN, VK_TEAMS_CHAT_ID, VK_TEAMS_HOOK_URL
    TOKENS_LOADED = True
except ImportError:
    TOKENS_LOADED = False
    print("⚠️ vk_notifier: access_tokens.py not found or missing VK settings.")

def send_to_vk_teams(message):
    """
    Public function to send message to VK Teams.
    Returns True if successful, False otherwise.
    """
    if not TOKENS_LOADED:
        return False

    try:
        params = {
            "token": VK_TEAMS_TOKEN,
            "chatId": VK_TEAMS_CHAT_ID,
            "text": message[:4000]
        }
        
        response = requests.get(VK_TEAMS_HOOK_URL, params=params, verify=False)
        
        if response.status_code == 200:
            print("✅ Message sent to VK Teams successfully")
            return True
        else:
            print(f"❌ VK Teams GET error: {response.status_code} - {response.text}")
            return _send_alternative(params)
            
    except Exception as e:
        print(f"❌ Error sending to VK Teams: {e}")
        return _send_alternative(params)

def _send_alternative(params):
    try:
        response = requests.post(VK_TEAMS_HOOK_URL, data=params, verify=False)
        if response.status_code == 200:
            print("✅ Message sent to VK Teams (alternative POST method)")
            return True
        else:
            print(f"❌ VK Teams POST failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Alternative VK Teams error: {e}")
        return False

