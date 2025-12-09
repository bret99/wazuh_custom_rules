#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WAZUH SOC AI ANALYZER v3.6 - TARGETED ANALYSIS
==============================================
Features:
- Targeted Analysis (--user, --host support)
- Smart Threat Filtering
- Detailed Reports & Cluster Analysis
- Modular Notifications

Usage:
python soc_ai_v2.py --mode [global|ueba|host] --file <json> [--user <name>] [--host <name>]
"""

import json
import os
import smtplib
import sys
import argparse
import requests
import torch
import numpy as np
import ijson
import re
import traceback
import warnings
from email.message import EmailMessage
from datetime import datetime
from collections import defaultdict
from decimal import Decimal

# Machine Learning Imports
from transformers import AutoTokenizer, AutoModel
from scipy.spatial.distance import cdist
from sklearn.cluster import DBSCAN

# === OPTIONAL VK TEAMS IMPORT ===
try:
    from vk_notifier import send_to_vk_teams
    VK_ENABLED = True
except ImportError:
    print("⚠️ Module 'vk_notifier' not found. VK Teams notifications disabled.")
    VK_ENABLED = False
    def send_to_vk_teams(msg): return False

warnings.filterwarnings("ignore", category=UserWarning, module='scipy')
warnings.filterwarnings("ignore", category=UserWarning, module='numpy')

# Load Settings
try:
    from secret_tokens import (
        SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD, 
        EMAIL_RECIPIENTS, TOP_CRITICAL_EVENTS
    )
except ImportError:
    print("❌ Error: access_tokens.py not found or incomplete.")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================
MODEL_NAME = "jackaduma/SecRoBERTa" # Substitute for actual one
#MODEL_NAME = "cisco-ai/SecureBERT2.0-base"
EMBEDDING_CACHE_MAX_SIZE = 10000

# Cluster params
CLUSTERING_EPS = 0.4  # cluster flexibility
MIN_CLUSTER_SIZE = 2  # cluster min size
MAX_CLUSTERS_TO_SHOW = 5  # cluster max amount to show

MODES = {
    "global": {
        "report_title": "⚡️ GLOBAL INFRASTRUCTURE SECURITY REPORT",
        "email_prefix": "GLOBAL Security Report"
    },
    "ueba": {
        "report_title": "⚡️ UEBA USER BEHAVIOR REPORT",
        "email_prefix": "UEBA User Report"
    },
    "host": {
        "report_title": "⚡️ DEEP HOST SECURITY ANALYSIS",
        "email_prefix": "HOST Deep Analysis"
    }
}

# ============================================================================
# CLASSES & UTILS
# ============================================================================
class EmbeddingsProcessor:
    def __init__(self, model_name=MODEL_NAME):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.embeddings_cache = {}
        self.cache_size = 0
        self._load_model()

    def _load_model(self):
        try:
            print(f"🔄 Loading AI for embeddings: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True, legacy=False)
            self.model = AutoModel.from_pretrained(self.model_name, trust_remote_code=True, torch_dtype=torch.float32)
            self.model = self.model.to("cpu")
            self.model.eval()
            print("✅ AI embeddings model loaded successfully")
            return True
        except Exception as e:
            print(f"❌ Error loading embeddings model: {e}")
            return False

    def get_embedding(self, text, use_cache=True):
        if not text or not self.model: return None
        if use_cache and text in self.embeddings_cache: return self.embeddings_cache[text]
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                embedding = outputs.last_hidden_state.mean(dim=1)[0].detach().cpu().numpy()
            if use_cache and self.cache_size < EMBEDDING_CACHE_MAX_SIZE:
                self.embeddings_cache[text] = embedding
                self.cache_size += 1
            return embedding
        except Exception as e:
            print(f"❌ Error generating embedding: {e}")
            return None

    def find_correlated_events(self, event_descriptions):
        if len(event_descriptions) < 2: return {}
        print(f"🔄 Generating embeddings for {len(event_descriptions)} unique descriptions...")
        embeddings = []
        valid_indices = []
        for idx, desc in enumerate(event_descriptions):
            embedding = self.get_embedding(desc, use_cache=True)
            if embedding is not None:
                embeddings.append(embedding)
                valid_indices.append(idx)
        if len(embeddings) < 2: return {}
        
        embeddings_array = np.array(embeddings)
        distances = cdist(embeddings_array, embeddings_array, 'cosine')
        
        # Trying different params for best clusterization
        try:
            clustering = DBSCAN(eps=CLUSTERING_EPS, min_samples=MIN_CLUSTER_SIZE, metric='precomputed').fit(distances)
            labels = clustering.labels_
            
            # Clusterization stats counting
            unique_labels = set(labels)
            n_clusters = len([l for l in unique_labels if l != -1])  # -1 = noise
            
            print(f"   Clustering results: {n_clusters} clusters found, {list(labels).count(-1)} noise points")
            
            correlated_groups = defaultdict(list)
            noise_indices = []
            for embedding_idx, cluster_label in enumerate(labels):
                original_idx = valid_indices[embedding_idx]
                if cluster_label == -1: 
                    noise_indices.append(original_idx)
                else: 
                    correlated_groups[int(cluster_label)].append(original_idx)
                    
            return {
                "clusters": dict(correlated_groups), 
                "noise": noise_indices, 
                "cluster_count": n_clusters, 
                "noise_count": len(noise_indices),
                "total_points": len(labels)
            }
        except Exception as e:
            print(f"❌ Error in clustering: {e}")
            return {}

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal): return float(obj)
        return super(DecimalEncoder, self).default(obj)

def extract_user_info(event):
    user_fields = [
        event.get('data', {}).get('srcuser'), event.get('data', {}).get('src_user'),
        event.get('data', {}).get('dstuser'), event.get('data', {}).get('dst_user'),
        event.get('data', {}).get('un'), event.get('data', {}).get('gitlab_user'),
        event.get('data', {}).get('gitlab_username'), event.get('user'),
        event.get('data', {}).get('jira_creator'),
        event.get('data', {}).get('confluence_creator'),  event.get('syscheck', {}).get('uname_after'),
        event.get('data', {}).get('win', {}).get('eventdata', {}).get('targetUserName'),
        event.get('data', {}).get('win', {}).get('eventdata', {}).get('subjectUserName'),
    ]
    for user in user_fields:
        if user and user not in ['unknown', '']: return user
    if 'full_log' in event:
        match = re.search(r'user[:\s]+([\w\\\@\.\-]+)', str(event['full_log']).lower())
        if match: return match.group(1)
    return 'unknown'

def extract_ip_info(event):
    ip_fields = [
        event.get('srcip'), event.get('data', {}).get('srcip'),
        event.get('src_ip'), event.get('data', {}).get('src_ip'),
        event.get('data', {}).get('dstip'), event.get('ip'),
        event.get('data', {}).get('dst_ip'),
        event.get('data', {}).get('win', {}).get('eventdata', {}).get('ipAddress'),
    ]
    for ip in ip_fields:
        if ip and ip not in ['unknown', ''] and re.match(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', ip): return ip
    return 'unknown'

def extract_host_info(event):
    """
    Extracts host/agent name from multiple possible fields.
    """
    # 1. Standard Agent Name
    agent_name = event.get('agent', {}).get('name')
    if agent_name and agent_name not in ['unknown', '']:
        return agent_name
        
    # 2. Data fields
    data = event.get('data', {})
    host_fields = [
        data.get('dhost'), 
        data.get('src_host'), 
        data.get('dst_host'),
        data.get('hostname')
    ]
    
    # 3. Windows Specific
    win_data = data.get('win', {}).get('eventdata', {})
    host_fields.append(win_data.get('workstationName'))
    host_fields.append(win_data.get('workstation'))

    for h in host_fields:
        if h and h not in ['unknown', '']:
            return h
            
    return 'unknown'

def extract_url_fields(event):
    data = event.get('data', {}) or {}
    url = data.get('url_address') or data.get('url') or data.get('request')
    user = data.get('url_user') or data.get('http_user')
    time = data.get('url_time') or data.get('event_time') or event.get('@timestamp', '')
    if not url and 'full_log' in event:
        m = re.search(r'(https?://[^\s"]+)', str(event['full_log']))
        if m: url = m.group(1)
    return {"url_address": url or 'unknown', "url_user": user or 'unknown', "url_time": time}

def extract_event_details(event):
    details = {
        'timestamp': event.get('@timestamp', ''),
        'agent': event.get('agent', {}).get('name', 'unknown'),
        'rule_level': event.get('rule', {}).get('level', 0),
        'rule_description': event.get('rule', {}).get('description', ''),
        'location': event.get('GeoLocation', {}).get('location', 'unknown'),
        'geo_location': event.get('GeoLocation', {}).get('country_name', 'unknown')
    }
    if 'data' in event and 'win' in event['data'] and 'eventdata' in event['data']['win']:
        details.update(event['data']['win']['eventdata'])
    def convert(obj):
        if isinstance(obj, Decimal): return float(obj)
        if isinstance(obj, dict): return {k: convert(v) for k, v in obj.items()}
        return obj
    return convert(details)

def analyze_large_json_file(file_path, target_user=None, target_host=None):
    """
    Analyzer with support for --user and --host filtering.
    FIXED: Now correctly detects failed authentications like soc_ai.py
    """
    stats = {
        'total_events': 0, 'by_level': defaultdict(int), 'by_ip': defaultdict(int),
        'by_user': defaultdict(int), 'critical_events': [], 'timeline': defaultdict(int),
        'failed_logons': 0, 'suspicious_ips': defaultdict(int), 'suspicious_users': defaultdict(int),
        'event_details': [], 'by_url_address': defaultdict(int), 'by_url_user': defaultdict(int),
        'failed_auth_sources': defaultdict(int), 'failed_auth_users': defaultdict(int),
        'unique_threats': {},
        'by_agent': defaultdict(int),
        'by_location': defaultdict(int)
    }
    
    # Pre-process target strings for case-insensitive matching
    t_user = target_user.lower() if target_user else None
    t_host = target_host.lower() if target_host else None
    
    try:
        print(f"📂 Starting file analysis: {file_path}")
        if t_user: print(f"🎯 Filtering for USER: {target_user}")
        if t_host: print(f"🎯 Filtering for HOST: {target_host}")

        with open(file_path, 'r', encoding='utf-8') as f:
            for event in ijson.items(f, 'item'):
                
                # --- EXTRACT ---
                user = extract_user_info(event)
                host = extract_host_info(event)
                
                # --- FILTER LOGIC ---
                # Skip event if target_user is set AND doesn't match
                if t_user:
                    if user == 'unknown' or t_user not in user.lower():
                        continue
                
                # Skip event if target_host is set AND doesn't match
                if t_host:
                    if host == 'unknown' or t_host not in host.lower():
                        continue
                
                # --- PROCESS MATCHING EVENT ---
                stats['total_events'] += 1
                
                ip = extract_ip_info(event)
                url_fields = extract_url_fields(event)
                details = extract_event_details(event)
                
                # Levels
                level = event.get('rule', {}).get('level', 0)
                rule_desc = str(event.get('rule', {}).get('description', '')).strip()
                if isinstance(level, (int, float, Decimal)): 
                    level = int(level)
                    stats['by_level'][level] += 1
                
                # Aggregations
                if ip != 'unknown': stats['by_ip'][ip] += 1
                if user != 'unknown': stats['by_user'][user] += 1
                if url_fields["url_address"] != 'unknown': stats['by_url_address'][url_fields["url_address"]] += 1
                
                # Collect agent and location stats
                agent = event.get('agent', {}).get('name', 'unknown')
                stats['by_agent'][agent] += 1
                location = event.get('location', 'unknown')
                stats['by_location'][location] += 1
                
                # FIXED: Enhanced failed auth detection (same as soc_ai.py)
                status = str(event.get('status', '')).lower()
                outcome = str(event.get('outcome', '')).lower()
                desc_lower = rule_desc.lower()
                
                # Use the same logic as soc_ai.py
                is_failed = ('fail' in status or 'fail' in outcome or 'fail' in desc_lower or
                            'failure' in status or 'failure' in outcome or
                            'unsuccessful' in status or 'unsuccessful' in outcome or
                            'denied' in status or 'denied' in outcome or 'error' in desc_lower)
                
                if is_failed:
                    stats['failed_logons'] += 1
                    if ip != 'unknown': 
                        stats['suspicious_ips'][ip] += 1
                        stats['failed_auth_sources'][ip] += 1
                    if user != 'unknown': 
                        stats['suspicious_users'][user] += 1
                        stats['failed_auth_users'][user] += 1

                # Smart Threat Filtering
                # 1. Exclude noise
                is_noise = any(x in desc_lower for x in [
                    'msedgewebview2.exe', 'teams.exe', 'update.exe', 'openconsole.exe',
                    'settingsynchost.exe', 'listened ports status', 'port:', 'local ip:'
                ])
                
                # 2. Prioritize critical info
                is_critical = (level >= 10)
                is_high_threat = (level >= 7 and not is_noise)
                is_attack_keyword = any(x in desc_lower for x in [
                    'malware', 'trojan', 'rootkit', 'promiscuous', 'attack', 'exploit', 
                    'brute force', 'adware', 'spyware', 'ransomware'
                ])
                
                is_interesting = is_critical or is_high_threat or is_attack_keyword or (is_failed and not is_noise)
                
                if is_interesting and rule_desc:
                    if rule_desc not in stats['unique_threats']:
                        stats['unique_threats'][rule_desc] = {'count': 0, 'level': level}
                    stats['unique_threats'][rule_desc]['count'] += 1

                # Critical Events List
                if level >= 8 and len(stats['critical_events']) < TOP_CRITICAL_EVENTS:
                    stats['critical_events'].append(event)
                
                if len(stats['event_details']) < 2000:
                    details['user'] = user
                    details['ip'] = ip
                    details.update(url_fields)
                    stats['event_details'].append(details)

        print(f"✅ Analysis completed. Matched events: {stats['total_events']}")
        print(f"🔐 Failed authentications detected: {stats['failed_logons']}")
        print(f"🧠 Unique interesting patterns: {len(stats['unique_threats'])}")
        return stats
    except Exception as e:
        print(f"❌ Error analyzing JSON file: {e}")
        traceback.print_exc()
        return stats

def generate_report_text(stats, mode_config, correlations_data=None, event_desc_map=None, target_user=None, target_host=None):
    """
    Generates FULL detailed report with formatting as requested.
    SHOWS MULTIPLE CLUSTERS if detected.
    """
    title = mode_config['report_title']
    
    # Modify title if filtered
    context_info = ""
    if target_user: context_info += f" [User: {target_user}]"
    if target_host: context_info += f" [Host: {target_host}]"
    if context_info: title += context_info

    # 1. HEADER
    report = f"{title}\n"
    report += "=" * 70 + "\n\n"
    
    # 2. GENERAL STATS
    report += f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    report += f"📊 Total events: {stats['total_events']:,}\n\n"
    
    # Add threat level distribution
    if stats['by_level']:
        report += "📈 Threat level distribution:\n"
        for level, count in sorted(stats['by_level'].items()):
            report += f"• Level {level}: {count:,} events\n"
        report += "\n"
    
    # Add high-level events summary
    high_level_events = sum(count for level, count in stats['by_level'].items() if level >= 8)
    report += f"🚨 High-level events (level ≥ 8): {high_level_events:,}\n\n"
    
    # 3. FAILED AUTHENTICATION DETAILS
    if stats['failed_logons'] > 0:
        report += f"🔐 Failed login attempts: {stats['failed_logons']:,}\n"
        
        # Top users with failed authentications
        if stats['failed_auth_users']:
            report += "🔓 Top 5 users with failed authentications:\n"
            top_failed_users = sorted(stats['failed_auth_users'].items(), key=lambda x: x[1], reverse=True)[:5]
            for user, count in top_failed_users:
                report += f"• {user}: {count} failed attempts\n"
        
        # Top sources of failed authentications
        if stats['failed_auth_sources']:
            report += "🌐 Top 5 sources of failed authentications:\n"
            top_failed_sources = sorted(stats['failed_auth_sources'].items(), key=lambda x: x[1], reverse=True)[:5]
            for source, count in top_failed_sources:
                report += f"• {source}: {count} failed attempts\n"
        report += "\n"
    
    # 4. CORRELATION SECTION - ПОКАЗЫВАЕМ ВСЕ КЛАСТЕРЫ
    report += "🔗 EVENT CORRELATION ANALYSIS & CHAINS\n"
    report += "-" * 70 + "\n"
    
    if correlations_data and correlations_data['cluster_count'] > 0:
        report += f"⚠️ CLUSTERS DETECTED: {correlations_data['cluster_count']}\n"
        report += f"   Total events analyzed: {correlations_data.get('total_points', 'N/A')}\n"
        report += f"   Noise points (unclustered): {correlations_data.get('noise_count', 0)}\n"
        report += "   Possible multi-stage attacks or coordinated activities found.\n\n"
        
        if event_desc_map:
            clusters_shown = 0
            for cluster_id, indices in sorted(correlations_data['clusters'].items()):
                clusters_shown += 1
                
                # Show only first MAX_CLUSTERS_TO_SHOW of clusters
                if clusters_shown > MAX_CLUSTERS_TO_SHOW:
                    remaining = correlations_data['cluster_count'] - MAX_CLUSTERS_TO_SHOW
                    report += f"... [{remaining} additional clusters not shown] ...\n\n"
                    break
                
                cluster_events = list(set([event_desc_map[i] for i in indices]))
                total_unique = len(cluster_events)
                
                report += f"🔸 CLUSTER #{cluster_id} - {total_unique} unique event types ({len(indices)} total occurrences)\n"
                
                # Events sorting due to frequences and levels
                event_counts = {}
                for idx in indices:
                    desc = event_desc_map[idx]
                    if desc not in event_counts:
                        event_counts[desc] = 0
                    event_counts[desc] += 1
                
                # Show cluster top events
                display_limit = 8
                sorted_events = sorted(event_counts.items(), key=lambda x: x[1], reverse=True)
                
                for i, (desc, count) in enumerate(sorted_events):
                    if i >= display_limit:
                        remaining = len(sorted_events) - display_limit
                        report += f"... and {remaining} more events ...\n"
                        break
                    report += f"• {desc} ({count}x)\n"
                
                # Cluster analize for recommendations
                cluster_text = " ".join([desc.lower() for desc in cluster_events])
                rec = "Investigate anomalies."
                
                if "fail" in cluster_text and "success" in cluster_text:
                    rec = "🚨 Possible Brute-force + Success pattern."
                elif "promiscuous" in cluster_text:
                    rec = "⚠️ Sniffing detected (Promiscuous mode). Check network interfaces."
                elif "rootkit" in cluster_text or "malware" in cluster_text:
                    rec = "🚨 CRITICAL: Malware/Rootkit signs. Isolate affected hosts immediately."
                elif "brute" in cluster_text or "force" in cluster_text:
                    rec = "🚨 Brute-force attack pattern detected."
                elif "exec" in cluster_text or "process" in cluster_text:
                    rec = "⚠️ Suspicious process execution pattern."
                elif "scan" in cluster_text or "port" in cluster_text:
                    rec = "⚠️ Network scanning activity detected."
                elif "web" in cluster_text and ("error" in cluster_text or "500" in cluster_text):
                    rec = "⚠️ Web application attacks or errors detected."
                
                report += f"👉 Recommendation: {rec}\n\n"
    else:
        report += "✅ No suspicious clusters detected.\n\n"

    # 5. TOP ACTIVITY SECTION
    report += "🎯 TOP SUSPICIOUS ACTIVITY\n"
    report += "-" * 70 + "\n\n"
    
    # Top IPs
    if stats['by_ip']:
        report += "🌐 Top-10 IP addresses by activity:\n"
        top_ips = sorted(stats['by_ip'].items(), key=lambda x: x[1], reverse=True)[:10]
        for ip, count in top_ips:
            failed = stats['failed_auth_sources'].get(ip, 0)
            report += f"• {ip}: {count} events ({failed} failed auth)\n"
        report += "\n"

    # Top Users
    if stats['by_user']:
        report += "👤 Top-10 users by activity:\n"
        top_users = sorted(stats['by_user'].items(), key=lambda x: x[1], reverse=True)[:10]
        for user, count in top_users:
            failed = stats['failed_auth_users'].get(user, 0)
            report += f"• {user}: {count} events ({failed} failed auth)\n"
        report += "\n"

    # 6. CRITICAL PREVIEW
    if stats['critical_events']:
        report += "🚨 CRITICAL EVENTS PREVIEW\n"
        report += "-" * 70 + "\n"
        for i, event in enumerate(stats['critical_events'][:5], 1):
            desc = event.get('rule', {}).get('description', 'N/A')
            report += f"{i}. {desc}\n"
        report += "\n"

    report += "⚠️ AUTOMATED REPORT - VERIFY FINDINGS\n"
    report += "-" * 70 + "\n"
    
    return report

def send_email(subject, body, recipients=None):
    if recipients is None: recipients = EMAIL_RECIPIENTS
    success = 0
    for recipient in recipients:
        try:
            msg = EmailMessage()
            msg.set_content(body); msg['Subject'] = subject
            msg['From'] = EMAIL_FROM; msg['To'] = recipient
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls(); server.login(EMAIL_FROM, EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"✉️ Email sent to: {recipient}"); success += 1
        except Exception as e: print(f"❌ Error sending email to {recipient}: {e}")
    return success, len(recipients)

# ============================================================================
# MAIN
# ============================================================================
def main():
    parser = argparse.ArgumentParser(description='SOC AI Analyzer v3.6')
    parser.add_argument('--mode', '-m', choices=['global', 'ueba', 'host'], required=True)
    parser.add_argument('--file', '-f', required=True)
    parser.add_argument('--user', '-u', required=False, help='Target specific User')
    parser.add_argument('--host', '-H', required=False, help='Target specific Host')
    args = parser.parse_args()
    
    if not os.path.exists(args.file): sys.exit(f"❌ File {args.file} not found")
    mode_config = MODES[args.mode]

    try:
        print(f"🔧 Starting SOC AI in [{args.mode.upper()}] mode")
        embeddings_processor = EmbeddingsProcessor()
        
        # --- PASS FILTERS ---
        print("\n📋 Step 1: Analyzing JSON data...")
        stats = analyze_large_json_file(args.file, target_user=args.user, target_host=args.host)
        
        if stats['total_events'] == 0:
            print("⚠️ No events matched your filter criteria. Exiting.")
            sys.exit(0)

        print("\n🤖 Step 2: AI Correlation Analysis...")
        correlations_data = None
        
        threats_list = [(desc, data['level'], data['count']) for desc, data in stats['unique_threats'].items()]
        threats_list.sort(key=lambda x: (x[1], x[2]), reverse=True)
        top_threat_descriptions = [t[0] for t in threats_list[:300]]
        
        print(f"   Selected {len(top_threat_descriptions)} critical unique patterns for AI.")
        
        if top_threat_descriptions:
            correlations_data = embeddings_processor.find_correlated_events(top_threat_descriptions)
        
        # --- GENERATE REPORT ---
        report_text = generate_report_text(
            stats, 
            mode_config, 
            correlations_data, 
            top_threat_descriptions, 
            target_user=args.user, 
            target_host=args.host
        )
        
        print("\n📤 Step 3: Sending notifications...")
        subject_prefix = f"🔒 {mode_config['email_prefix']}"
        if args.user: subject_prefix += f" [User: {args.user}]"
        if args.host: subject_prefix += f" [Host: {args.host}]"
        
        subject = f"{subject_prefix} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        email_success, email_total = send_email(subject, report_text)

        if VK_ENABLED:
            print("📨 Preparing VK Teams notification...")
            vk_msg = f"🛡️ SOC AI: {mode_config['email_prefix']}\n"
            if args.user: vk_msg += f"🎯 Target: {args.user}\n"
            if args.host: vk_msg += f"🎯 Target: {args.host}\n"
            vk_msg += f"\n📊 Events: {stats['total_events']:,}\n"
            vk_msg += f"🚨 Critical: {len(stats['critical_events'])}\n"
            vk_msg += f"🔐 Failed Logins: {stats['failed_logons']:,}\n"
            
            # Add high-level events to VK message
            high_level_events = sum(count for level, count in stats['by_level'].items() if level >= 8)
            vk_msg += f"🚨 High-level events (level ≥ 8): {high_level_events:,}\n"
            
            if correlations_data:
                vk_msg += f"🔗 Clusters: {correlations_data['cluster_count']}\n"

            # Add top failed auth users to VK message
            if stats['failed_auth_users']:
                top_failed_users = sorted(stats['failed_auth_users'].items(), key=lambda x: x[1], reverse=True)[:3]
                vk_msg += "\n🔓 Top Failed Auth Users:\n"
                for user, count in top_failed_users:
                    vk_msg += f" • {user}: {count} fails\n"
            
            # Add top failed auth sources to VK message
            if stats['failed_auth_sources']:
                top_failed_sources = sorted(stats['failed_auth_sources'].items(), key=lambda x: x[1], reverse=True)[:3]
                vk_msg += "\n🌐 Top Failed Auth Sources:\n"
                for source, count in top_failed_sources:
                    vk_msg += f" • {source}: {count} fails\n"
            
            vk_msg += f"\n📧 Full report sent to {email_success}/{email_total} recipients"
            send_to_vk_teams(vk_msg)
        else:
            print("⏩ VK Teams skipped.")

        print("\n✅ Analysis Completed.")

    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        traceback.print_exc()
        if VK_ENABLED: 
            try: send_to_vk_teams(f"❌ SOC AI Failed: {str(e)}")
            except: pass
        sys.exit(1)

if __name__ == "__main__":
    try: import ijson, scipy, sklearn
    except ImportError: os.system(f"{sys.executable} -m pip install ijson scipy scikit-learn requests transformers torch")
    main()
