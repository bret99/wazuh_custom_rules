import sys
import json
import requests

# CHAT_ID is initialized
CHAT_ID = "" # Isert here actual one

# Read configuration parameters
alert_file_path = sys.argv[1]
hook_url = sys.argv[3]

# Read the alert file with UTF-8 encoding to handle Cyrillic characters
try:
    with open(alert_file_path, 'r', encoding='utf-8') as alert_file:
        alert_json = json.load(alert_file)
except UnicodeDecodeError:
    print("File decoding error. Be sure that file is in UTF-8 coding.")
    sys.exit(1)

# Extract data fields
alert_level = alert_json['rule']['level'] if 'level' in alert_json['rule'] else "N/A"
description = alert_json['rule']['description'] if 'description' in alert_json['rule'] else "N/A"
agent = alert_json['agent']['name'] if 'name' in alert_json['agent'] else "N/A"

# Function to map alert level to risk level and emoji
def get_risk_level_and_emoji(level):
    if level == 11:
        return "moderate", "✅"  # Green checkmark
    elif level == 12:
        return "high", "🔥"  # Fire
    elif level >= 13:
        return "critical", "❌"  # Red cross
   
# Map alert level to risk level and emoji
risk_level_text, risk_level_emoji = get_risk_level_and_emoji(int(alert_level))

# Generate formatted message
formatted_message = (
    f"<b>🔒Risk level:</b> {risk_level_text} {risk_level_emoji}\n"
    f"<b>📌Description:</b> {description}\n"
    f"<b>👤Source:</b> {agent}"
)

# Generate request for Information Security Department
msg_data = {
    'chat_id': CHAT_ID,
    'text': formatted_message,
    'parse_mode': 'HTML'  # Enable HTML parsing for formatting
}

headers = {'Content-Type': 'application/json; charset=UTF-8', 'Accept-Charset': 'UTF-8'}

requests.post(hook_url, headers=headers, json=msg_data)

# Optionally print the response for debugging
#print(response.status_code)
#print(response.text)

sys.exit(0)
