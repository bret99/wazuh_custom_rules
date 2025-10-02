#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import smtplib
import sys
from email.message import EmailMessage
from datetime import datetime
import requests
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import ijson
from collections import defaultdict
import re
from decimal import Decimal
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='urllib3')
from secret_tokens import (
        VK_TEAMS_TOKEN,
        VK_TEAMS_CHAT_ID,
        VK_TEAMS_HOOK_URL,
        SMTP_SERVER,
        SMTP_PORT,
        EMAIL_FROM,
        EMAIL_PASSWORD,
        EMAIL_RECIPIENTS,
        MODEL_NAME,
        FALLBACK_MODEL,
        TOP_CRITICAL_EVENTS
    )

# Import external functions (commented for user choice)
# from send_vk_teams import send_to_vk_teams
# from send_telegram import send_to_telegram

# Load SYSTEM_PROMPT from external file
try:
    with open('soc_prompt.txt', 'r', encoding='utf-8') as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    print("Warning: soc_prompt.txt not found, using default prompt")
    SYSTEM_PROMPT = (
        "You are an experienced and meticulous cybersecurity specialist, a virtual SOC analyst at L2 level. "
        "Your main task is to conduct detailed analysis of security logs to identify Indicators of Compromise (IoC) and anomalous activity.\n\n"
        "**Context:**\n"
        "You receive a JSON object containing a stream of security events (e.g., authentication logs, network connections, "
        "Windows Event Log events, Linux audit logs, and others). Events may be fragmented and noisy. Your goal is to filter out informational noise and highlight suspicious activities that require further investigation.\n\n"
        "**Step-by-step task execution instructions:**\n\n"
        "1.  **Primary analysis and filtering:**\n"
        "    *   Carefully study all provided fields in the JSON object (e.g.: @timestamp, agent, data, full_log, rule, location, GeoLocation). Pay attention to nested data structures in JSON objects.\n"
        "    *   Conduct mental correlation analysis of events, identifying connections between them.\n"
        "    *   Identify a pool of suspicious events based on the following criteria:\n"
        "        *   **Authentication anomalies:** Failed login attempts (Failed Logon), multiple successful logins from different IP addresses in a short time, suspicious logon types (e.g., Logon Type 8 - NetworkClearText), logins during non-working hours (5:00 - 10:00 UTC).\n"
        "        *   **Network anomalies:** Connections to known malicious or suspicious IP addresses/domains (e.g., addresses in country ranges not typical for company activities), connections to non-standard ports.\n"
        "        *   **Account behavior anomalies:** Privilege escalation, execution of suspicious processes under user accounts, activity of inactive or service accounts.\n"
        "        *   **Other IoC:** Any other events that, based on your analyst experience, may indicate reconnaissance, lateral movement, data exfiltration, or code execution.\n\n"
        "2.  **Grouping and investigation:**\n"
        "    *   Group filtered suspicious events by key entities:\n"
        "        *   **By user account (`user_name`)**\n"
        "        *   **By source IP address (`ip_address`)**\n"
        "    *   For each group, prepare a brief but informative summary.\n\n"
        "3.  **Summary requirements for each entity:**\n"
        "    *   **For user account (`user_name`):**\n"
        "        *   Specify the account name.\n"
        "        *   List key suspicions against it (e.g.: \"Multiple failed login attempts followed by successful login\", \"Login from geographically uncharacteristic location\", \"Suspicious command line executed by the user\").\n"
        "        *   Specify the time range of activity and number of related events.\n"
        "        *   List all suspicious IP addresses from which activity was conducted for this account.\n"
        "        *   Assess the risk level (Low, Medium, High) and provide recommended actions for the analyst (e.g.: \"Password reset required\", \"Initiate endpoint verification\", \"Add to monitoring for further suspicious activity\").\n\n"
        "    *   **For IP address (`ip_address`):**\n"
        "        *   Specify the IP address itself.\n"
        "        *   Provide crowdsourced reputation assessment (if there are indicators in the data, e.g.: \"IP from Russia, activity related to brute force\", \"IP from AWS subnet, possible command and control infrastructure\").\n"
        "        *   List all compromised or attacked accounts associated with this IP.\n"
        "        *   Describe the type of activity originating from this address (e.g.: \"Brute-force attack on Administrator account\", \"Successful authentication and subsequent PowerShell execution\").\n"
        "        *   Specify the time range of the attack.\n"
        "        *   Assess the threat level (Low, Medium, High) and provide recommendations (e.g.: \"Add IP to firewall blacklist\", \"Raise incident\").\n\n"
        "**Output format:**\n"
        "Your response should be clearly structured and easily readable for a tired analyst at 3 AM. Use the following template:\n\n"
        "### Security Log Analysis Results\n\n"
        "**Total events processed:** [X]\n\n"
        "**Suspicious events identified:** [Y]\n\n"
        "---\n\n"
        "#### User Account Summary:\n\n"
        "**Account:** `[user_name_1]`\n"
        "*   **Risk Level:** [Low/Medium/High]\n"
        "*   **Time Range:** [2023-11-15 03:14:15 - 2023-11-15 03:50:22]\n"
        "*   **Event Count:** [Z]\n"
        "*   **Key Suspicions:**\n"
        "    *   Suspicion 1 (e.g., 10 failed login attempts in 2 minutes).\n"
        "    *   Suspicion 2 (e.g., successful login from IP 185.XXX.XXX.XXX, which appears in threat lists).\n"
        "*   **Associated Suspicious IP Addresses:** `[ip_address_1]`, `[ip_address_2]`\n"
        "*   **Recommendations:** [Recommendation 1], [Recommendation 2].\n\n"
        "---\n\n"
        "#### IP Address Summary:\n\n"
        "**IP Address:** `[ip_address_1]`\n"
        "*   **Threat Level:** [Low/Medium/High]\n"
        "*   **Reputation Assessment:** [Brief assessment based on context]\n"
        "*   **Activity Time Range:** [2023-11-15 03:14:15 - 2023-11-15 03:50:22]\n"
        "*   **Attack Targets/Compromised Accounts:** `[user_name_1]`, `[user_name_2]`\n"
        "*   **Activity Type:** [Description, e.g., Brute-force attack]\n"
        "*   **Recommendations:** [Add to blacklist], [Initiate investigation].\n\n"
        "---\n\n"
        "**General Recommendations and Next Steps:** [Brief final conclusion about the entire incident and what the analyst should do next]."
    )

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def load_model_and_tokenizer():
    """
    Load model and tokenizer with error handling
    """
    models_to_try = [MODEL_NAME, FALLBACK_MODEL]
    
    for model_name in models_to_try:
        try:
            print(f"Attempting to load model: {model_name}")
            
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
                legacy=False
            )
            
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="auto",
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                trust_remote_code=True
            )
            
            print(f"Model {model_name} successfully loaded")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Device set to use {device}")
            return tokenizer, model
            
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            continue
    
    raise Exception("Failed to load any model")

def extract_user_info(event):
    """
    Extract user information from various fields in the event
    """
    user_fields = [
        # Direct fields
        event.get('data', {}).get('srcuser'),
        event.get('data', {}).get('src_user'),
        event.get('data', {}).get('dstuser'),
        event.get('data', {}).get('dst_user'),
        event.get('data', {}).get('un'),
        event.get('data', {}).get('gitlab_user'),
        event.get('data', {}).get('gitlab_username'),
        event.get('user'),
        
        # Nested Windows eventdata fields
        event.get('data', {}).get('win', {}).get('eventdata', {}).get('targetUserName'),
        event.get('data', {}).get('win', {}).get('eventdata', {}).get('subjectUserName'),
    ]
    
    # Find first non-empty value
    for user in user_fields:
        if user and user != 'unknown' and user != '':
            return user
    
    # Additional search in full_log
    if 'full_log' in event:
        full_log = event['full_log'].lower()
        user_patterns = [
            r'user[:\s]+([\w\\\\@\.\-]+)',
            r'username[:\s]+([\w\\\\@\.\-]+)',
            r'account[:\s]+([\w\\\\@\.\-]+)',
            r'login[:\s]+([\w\\\\@\.\-]+)',
        ]
        
        for pattern in user_patterns:
            match = re.search(pattern, full_log)
            if match:
                return match.group(1)
    
    return 'unknown'

def extract_ip_info(event):
    """
    Extract IP information from various fields in the event
    """
    ip_fields = [
        # Direct fields
        event.get('srcip'),
        event.get('data', {}).get('srcip'),
        event.get('data', {}).get('src_ip'),
        event.get('data', {}).get('dstip'),
        event.get('data', {}).get('dst_ip'),
        event.get('data', {}).get('remote_addr'),
        event.get('data', {}).get('src_host'),
        event.get('ip'),
        
        # Nested Windows eventdata fields
        event.get('data', {}).get('win', {}).get('eventdata', {}).get('ipAddress'),
    ]
    
    # Find first non-empty value
    for ip in ip_fields:
        if ip and ip != 'unknown' and ip != '':
            # Make sure it looks like an IP address
            if re.match(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', ip):
                return ip
    
    # Additional search in full_log
    if 'full_log' in event:
        full_log = event['full_log']
        ip_match = re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', full_log)
        if ip_match:
            return ip_match.group(0)
    
    return 'unknown'

def convert_decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    return obj

def extract_event_details(event):
    """
    Extract detailed information from event for better analysis
    """
    details = {
        'timestamp': event.get('@timestamp', ''),
        'agent': event.get('agent', {}).get('name', 'unknown'),
        'rule_level': event.get('rule', {}).get('level', 0),
        'rule_description': event.get('rule', {}).get('description', ''),
        'location': event.get('location', ''),
        'geo_location': event.get('GeoLocation', {}),
        'logon_type': None,
        'status': None,
        'process_name': None
    }
    
    # Extract Windows event specific details
    if 'data' in event and 'win' in event['data'] and 'eventdata' in event['data']['win']:
        eventdata = event['data']['win']['eventdata']
        details.update({
            'logon_type': eventdata.get('logonType'),
            'status': eventdata.get('status'),
            'process_name': eventdata.get('processName'),
            'workstation': eventdata.get('workstationName'),
            'authentication_package': eventdata.get('authenticationPackageName')
        })
    
    # Convert Decimal to float for JSON serialization
    details = convert_decimal_to_float(details)
    
    return details

def analyze_large_json_file(file_path):
    """
    Analyze large JSON file with aggregation and statistics
    Returns aggregated data for AI analysis
    """
    stats = {
        'total_events': 0,
        'by_level': defaultdict(int),
        'by_ip': defaultdict(int),
        'by_user': defaultdict(int),
        'critical_events': [],
        'timeline': defaultdict(int),
        'failed_logons': 0,
        'suspicious_ips': defaultdict(int),
        'suspicious_users': defaultdict(int),
        'event_details': [],
        'by_agent': defaultdict(int),
        'by_location': defaultdict(int),
        'failed_auth_users': defaultdict(int),  # New: users with failed authentications
        'failed_auth_sources': defaultdict(int),  # New: sources of failed authentications
    }
    
    try:
        print(f"Starting file analysis: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Use ijson for stream processing
            events = ijson.items(f, 'item')
            
            for event in events:
                stats['total_events'] += 1
                
                # Extract user and IP information
                user = extract_user_info(event)
                ip = extract_ip_info(event)
                details = extract_event_details(event)
                
                # Collect statistics by levels
                level = event.get('rule', {}).get('level', 0)
                if isinstance(level, (int, float, Decimal)):
                    level_int = int(level)
                    stats['by_level'][level_int] += 1
                
                # Collect statistics by IP
                if ip != 'unknown':
                    stats['by_ip'][ip] += 1
                
                # Collect statistics by users
                if user != 'unknown':
                    stats['by_user'][user] += 1
                
                # Collect statistics by agents
                agent = event.get('agent', {}).get('name', 'unknown')
                stats['by_agent'][agent] += 1
                
                # Collect statistics by locations
                location = event.get('location', 'unknown')
                stats['by_location'][location] += 1
                
                # Collect time statistics
                timestamp = event.get('@timestamp', '')[:13]  # Take only hour
                if timestamp:
                    stats['timeline'][timestamp] += 1
                
                # Count failed logins
                status = str(event.get('status', '')).lower()
                outcome = str(event.get('outcome', '')).lower()
                rule_desc = str(event.get('rule', {}).get('description', '')).lower()
                
                is_failed_auth = ('fail' in status or 'fail' in outcome or 'fail' in rule_desc or
                                 'failure' in status or 'failure' in outcome or
                                 'unsuccessful' in status or 'unsuccessful' in outcome or
                                 'denied' in status or 'denied' in outcome)
                
                if is_failed_auth:
                    stats['failed_logons'] += 1
                    if ip != 'unknown':
                        stats['suspicious_ips'][ip] += 1
                        stats['failed_auth_sources'][ip] += 1  # Record source
                    if user != 'unknown':
                        stats['suspicious_users'][user] += 1
                        stats['failed_auth_users'][user] += 1  # Record user
                
                # Select critical events for detailed analysis
                if level and level >= 8:  # High threat level
                    if len(stats['critical_events']) < TOP_CRITICAL_EVENTS:
                        stats['critical_events'].append(event)
                    else:
                        # Replace least critical event if current is more critical
                        min_level = min([e.get('rule', {}).get('level', 0) for e in stats['critical_events']])
                        if level > min_level:
                            for i, e in enumerate(stats['critical_events']):
                                if e.get('rule', {}).get('level', 0) == min_level:
                                    stats['critical_events'][i] = event
                                    break
                
                # Save event details for analysis
                details['user'] = user
                details['ip'] = ip
                stats['event_details'].append(details)
        
        print(f"Analysis completed. Processed events: {stats['total_events']}")
        return stats
        
    except Exception as e:
        print(f"Error analyzing JSON file: {e}")
        return stats

def prepare_ai_input(stats):
    """
    Prepare data for AI based on aggregated statistics
    """
    # Convert all data to be JSON serializable
    stats_serializable = convert_decimal_to_float(stats)
    
    ai_input = {
        "General Statistics": {
            "Total Events": stats_serializable['total_events'],
            "Threat Level Distribution": dict(sorted(stats_serializable['by_level'].items())),
            "Failed Login Attempts": stats_serializable['failed_logons'],
            "Hourly Activity (Peak Values)": dict(sorted(stats_serializable['timeline'].items(), key=lambda x: x[1], reverse=True)[:10])
        },
        "Top Suspicious IP Addresses": dict(sorted(stats_serializable['by_ip'].items(), key=lambda x: x[1], reverse=True)[:20]),
        "Top Suspicious Users": dict(sorted(stats_serializable['by_user'].items(), key=lambda x: x[1], reverse=True)[:20]),
        "Agent Distribution": dict(sorted(stats_serializable['by_agent'].items(), key=lambda x: x[1], reverse=True)[:10]),
        "Location Distribution": dict(sorted(stats_serializable['by_location'].items(), key=lambda x: x[1], reverse=True)[:10]),
        "Critical Events Count": len(stats_serializable['critical_events']),
        "Event Details Sample": stats_serializable['event_details'][:20]  # Reduced sample size
    }
    
    return ai_input

def analyze_with_transformers(events_json_path, stats):
    """
    Analyze log using huggingface transformers
    """
    try:
        tokenizer, model = load_model_and_tokenizer()

        # Create pipeline without specifying device, as model is already loaded with accelerate
        nlp = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=4096,
            temperature=0.3,
            do_sample=True,
            top_p=0.9,
            top_k=40
        )

        # Prepare data for AI
        ai_input = prepare_ai_input(stats)
        events_str = json.dumps(ai_input, ensure_ascii=False, indent=2, cls=DecimalEncoder)

        prompt = SYSTEM_PROMPT + "\n\nAggregated Security Data:\n" + events_str + "\n\nProvide your response strictly in the requested format."

        print("Starting response generation...")
        result = nlp(prompt, max_new_tokens=2048)[0]["generated_text"]
        
        if prompt in result:
            result = result.split(prompt)[-1].strip()
            
        return result
        
    except Exception as e:
        print(f"Error during AI analysis: {e}")
        return generate_fallback_analysis(stats)

def generate_fallback_analysis(stats):
    """
    Simple analysis without AI in case of error
    """
    analysis = "⚡️ SECURITY EVENT ANALYSIS (AGGREGATED)\n\n"
    analysis += f"📊 Total events: {stats['total_events']:,}\n"
    
    if stats['by_level']:
        analysis += "\n📈 Threat level distribution:\n"
        for level, count in sorted(stats['by_level'].items()):
            analysis += f"  • Level {level}: {count:,} events\n"
    
    if stats['by_ip']:
        analysis += "\n🌐 Top-10 IP addresses by activity:\n"
        top_ips = sorted(stats['by_ip'].items(), key=lambda x: x[1], reverse=True)[:10]
        for ip, count in top_ips:
            analysis += f"  • {ip}: {count:,} events\n"
    
    if stats['by_user']:
        analysis += "\n👤 Top-10 users by activity:\n"
        top_users = sorted(stats['by_user'].items(), key=lambda x: x[1], reverse=True)[:10]
        for user, count in top_users:
            analysis += f"  • {user}: {count:,} events\n"
    
    # Add extended information about failed authentications
    analysis += f"\n🔐 Failed login attempts: {stats['failed_logons']:,}\n"
    
    # Top 5 users with failed authentications
    if stats['failed_auth_users']:
        analysis += "🔓 Top 5 users with failed authentications:\n"
        top_failed_users = sorted(stats['failed_auth_users'].items(), key=lambda x: x[1], reverse=True)[:5]
        for user, count in top_failed_users:
            analysis += f"  • {user}: {count} failed attempts\n"
    
    # Top 5 sources of failed authentications
    if stats['failed_auth_sources']:
        analysis += "🌐 Top 5 sources of failed authentications:\n"
        top_failed_sources = sorted(stats['failed_auth_sources'].items(), key=lambda x: x[1], reverse=True)[:5]
        for source, count in top_failed_sources:
            analysis += f"  • {source}: {count} failed attempts\n"
    
    analysis += f"🚨 High-level events (level ≥ 8): {sum(count for level, count in stats['by_level'].items() if level >= 8):,}\n"
    
    # Add information about critical events
    if stats['critical_events']:
        analysis += f"\n🔴 Critical events found: {len(stats['critical_events'])}\n"
        for i, event in enumerate(stats['critical_events'][:5], 1):
            rule_desc = event.get('rule', {}).get('description', 'No description')
            analysis += f"  {i}. {rule_desc}\n"
    
    return analysis

def send_email(subject, body, recipients=None):
    """
    Send email with analysis results to multiple recipients
    """
    if recipients is None:
        recipients = EMAIL_RECIPIENTS
    
    success_count = 0
    total_count = len(recipients)
    
    for recipient in recipients:
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = EMAIL_FROM
            msg['To'] = recipient

            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.send_message(msg)
            
            print(f"Email sent successfully to: {recipient}")
            success_count += 1
            
        except Exception as e:
            print(f"Error sending email to {recipient}: {e}")
    
    return success_count, total_count

# Commented VK Teams function - moved to separate module
# def send_to_vk_teams(message):
#     """
#     Send message to VK Teams with correct format
#     """
#     try:
#         # Correct format for VK Teams API according to documentation
#         params = {
#             "token": VK_TEAMS_TOKEN,
#             "chatId": VK_TEAMS_CHAT_ID,
#             "text": message[:4000]  # Message length limit
#         }
        
#         # Send as query parameters, not as JSON body
#         response = requests.get(VK_TEAMS_HOOK_URL, params=params, verify=False)
        
#         if response.status_code == 200:
#             print("Message sent to VK Teams successfully")
#             return True
#         else:
#             print(f"Error sending to VK Teams: {response.status_code} - {response.text}")
#             # Try alternative sending method
#             return send_to_vk_teams_alternative(message)
            
#     except Exception as e:
#         print(f"Error sending to VK Teams: {e}")
#         return send_to_vk_teams_alternative(message)

# Commented Telegram function - moved to separate module
# def send_to_telegram(message):
#     """
#     Send message to Telegram
#     """
#     try:
#         # You need to set these variables in secret_tokens.py
#         from secret_tokens import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
        
#         url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
#         data = {
#             "chat_id": TELEGRAM_CHAT_ID,
#             "text": message[:4096],  # Telegram message limit
#             "parse_mode": "HTML"
#         }
        
#         response = requests.post(url, data=data, timeout=10)
#         if response.status_code == 200:
#             print("Message sent to Telegram successfully")
#             return True
#         else:
#             print(f"Error sending to Telegram: {response.status_code} - {response.text}")
#             return False
            
#     except Exception as e:
#         print(f"Error sending to Telegram: {e}")
#         return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_json_file>")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    if not os.path.exists(json_file_path):
        print(f"File {json_file_path} not found")
        sys.exit(1)
    
    try:
        # Step 1: Analyze JSON file and aggregate data
        print("Step 1: Analyzing JSON file and aggregating data...")
        stats = analyze_large_json_file(json_file_path)
        
        # Step 2: Analyze with AI
        print("Step 2: Performing AI analysis...")
        analysis_result = analyze_with_transformers(json_file_path, stats)
        
        # Step 3: Send results
        print("Step 3: Sending results...")
        
        # Send email to all recipients
        email_subject = f"Security Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        email_success_count, email_total_count = send_email(email_subject, analysis_result)
        
        # Uncomment the following lines if you want to use VK Teams and Telegram notifications
        # Send to VK Teams (short version)
        # teams_message = f"🔒 Security Analysis Complete\n\n"
        # teams_message += f"📊 Total Events: {stats['total_events']:,}\n"
        # teams_message += f"🚨 Critical Events: {len(stats['critical_events'])}\n"
        # teams_message += f"🔐 Failed Logins: {stats['failed_logons']}\n"
        
        # # Add information about top suspicious IPs
        # if stats['suspicious_ips']:
        #     top_suspicious_ips = sorted(stats['suspicious_ips'].items(), key=lambda x: x[1], reverse=True)[:3]
        #     teams_message += f"🌐 Top Suspicious IPs:\n"
        #     for ip, count in top_suspicious_ips:
        #         teams_message += f"  • {ip}: {count} events\n"
        
        # teams_message += f"\n📧 Full report sent to {email_success_count}/{email_total_count} recipients"
        
        # teams_success = send_to_vk_teams(teams_message)
        
        # # Send to Telegram
        # telegram_success = send_to_telegram(teams_message)
        
        print(f"\nAnalysis completed successfully!")
        print(f"Total events processed: {stats['total_events']}")
        print(f"Critical events found: {len(stats['critical_events'])}")
        print(f"Failed login attempts: {stats['failed_logons']}")
        print(f"Emails sent: {email_success_count}/{email_total_count}")
        
        # Uncomment if using VK Teams and Telegram
        # if teams_success:
        #     print("✓ VK Teams notification sent")
        # else:
        #     print("✗ VK Teams notification failed")
        
        # if telegram_success:
        #     print("✓ Telegram notification sent")
        # else:
        #     print("✗ Telegram notification failed")
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        error_msg = f"Security Analysis Failed: {str(e)}"
        # Uncomment if you want to send error notifications
        # send_to_vk_teams(error_msg)
        # send_to_telegram(error_msg)

if __name__ == "__main__":
    # Install ijson library if not present
    try:
        import ijson
    except ImportError:
        print("Installing ijson library...")
        os.system(f"{sys.executable} -m pip install ijson")
        import ijson
    
    main()
