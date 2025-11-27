#!/usr/bin/env python3
import os
import json
import sqlite3
import glob
import time
from datetime import datetime
import hashlib
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/systeminfocollect.log'),
        logging.StreamHandler()
    ]
)

class BrowserHistoryCollector:
    def __init__(self, output_file="/var/log/systeminfocollect.json"):
        self.output_file = output_file
        self.existing_hashes = self.load_existing_hashes()
        
    def load_existing_hashes(self):
        hashes = set()
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line.strip())
                                url_hash = hashlib.md5(
                                    f"{entry['url_time']}_{entry['url_address']}_{entry['url_browser']}".encode('utf-8')
                                ).hexdigest()
                                hashes.add(url_hash)
                            except (json.JSONDecodeError, KeyError):
                                continue
            except Exception as e:
                logging.error(f"Error loading existing hashes: {e}")
        return hashes
    
    def get_hash(self, url_time, url_address, url_browser):
        return hashlib.md5(f"{url_time}_{url_address}_{url_browser}".encode('utf-8')).hexdigest()
    
    def save_entry(self, url_time, url_address, url_browser, url_user):
        url_hash = self.get_hash(url_time, url_address, url_browser)
        
        if url_hash not in self.existing_hashes:
            entry = {
                "url_time": url_time,
                "url_address": url_address,
                "url_user": url_user,
                "url_browser": url_browser
            }
            
            try:
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                self.existing_hashes.add(url_hash)
                logging.info(f"New entry added: {url_address}")
                return True
            except Exception as e:
                logging.error(f"Error saving entry: {e}")
        return False
    
    def get_firefox_history(self, profile_path, profile_name, username):
        try:
            db_path = os.path.join(profile_path, 'places.sqlite')
            if not os.path.exists(db_path):
                return
            
            temp_db = f"/tmp/places_{int(time.time())}.sqlite"
            os.system(f"cp '{db_path}' '{temp_db}'")
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT datetime(h.visit_date/1000000, 'unixepoch') as visit_time, 
                       p.url, p.title
                FROM moz_places p
                JOIN moz_historyvisits h ON p.id = h.place_id
                ORDER BY h.visit_date DESC
            """)
            
            for visit_time, url, title in cursor.fetchall():
                browser_name = f"firefox_{profile_name}"
                self.save_entry(visit_time, url, browser_name, username)
            
            conn.close()
            os.remove(temp_db)
            
        except Exception as e:
            logging.error(f"Error processing Firefox history {profile_path}: {e}")
    
    def get_chromium_history(self, history_path, browser_name, username):
        try:
            if not os.path.exists(history_path):
                return
            
            temp_db = f"/tmp/chromium_{int(time.time())}.sqlite"
            os.system(f"cp '{history_path}' '{temp_db}'")
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT datetime(last_visit_time/1000000-11644473600, 'unixepoch') as visit_time, 
                       url, title
                FROM urls 
                ORDER BY last_visit_time DESC
            """)
            
            for visit_time, url, title in cursor.fetchall():
                self.save_entry(visit_time, url, browser_name, username)
            
            conn.close()
            os.remove(temp_db)
            
        except Exception as e:
            logging.error(f"Error processing Chromium history {history_path}: {e}")
    
    def get_webkit_history(self, history_path, browser_name, username):
        try:
            if not os.path.exists(history_path):
                return
            
            temp_db = f"/tmp/webkit_{int(time.time())}.sqlite"
            os.system(f"cp '{history_path}' '{temp_db}'")
            
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # For Epiphany
            cursor.execute("""
                SELECT datetime(last_visit_time, 'unixepoch') as visit_time, 
                       url, title
                FROM history 
                ORDER BY last_visit_time DESC
            """)
            
            for visit_time, url, title in cursor.fetchall():
                self.save_entry(visit_time, url, browser_name, username)
            
            conn.close()
            os.remove(temp_db)
            
        except Exception as e:
            logging.error(f"Error processing WebKit history {history_path}: {e}")
    
    def collect_all_history(self):
        logging.info("Starting browser history collection...")
        
        home_dirs = []
        if os.path.exists('/home'):
            home_dirs = [d for d in os.listdir('/home') if os.path.isdir(os.path.join('/home', d))]
        
        current_user = os.path.expanduser('~').split('/')[-1]
        if current_user not in home_dirs:
            home_dirs.append(current_user)
        
        for username in home_dirs:
            home_path = os.path.join('/home', username) if username != current_user else os.path.expanduser('~')
            
            firefox_like_browsers = [
                ('~/.mozilla/firefox', 'firefox'),
                ('~/.librewolf', 'librewolf'),
                ('~/.waterfox', 'waterfox'),
                ('~/.mozilla/icecat', 'icecat'),
                ('~/.basilisk', 'basilisk'),
                ('~/.floorp', 'floorp'),
                ('~/.zen', 'zen'),
                ('~/.palemoon', 'palemoon')
            ]
            
            for browser_path, browser_name in firefox_like_browsers:
                full_path = browser_path.replace('~', home_path)
                if os.path.exists(full_path):
                    for profile in glob.glob(os.path.join(full_path, '*')):
                        if os.path.isdir(profile):
                            profile_name = os.path.basename(profile)
                            self.get_firefox_history(profile, f"{browser_name}_{profile_name}", username)
            chromium_browsers = [
                ('~/.config/google-chrome/*/History', 'chrome'),
                ('~/.config/chromium/*/History', 'chromium'),
                ('~/.config/BraveSoftware/Brave-Browser/*/History', 'brave'),
                ('~/.config/opera/*/History', 'opera'),
                ('~/.config/vivaldi/*/History', 'vivaldi'),
                ('~/.config/microsoft-edge/*/History', 'edge'),
                ('~/.config/yandex-browser/*/History', 'yandex'),
                ('~/.config/slimjet/*/History', 'slimjet'),
                ('~/.config/falkon/profiles/*/browser-history.sqlite', 'falkon')
            ]
            
            for browser_pattern, browser_name in chromium_browsers:
                full_pattern = browser_pattern.replace('~', home_path)
                for history_file in glob.glob(full_pattern):
                    if os.path.exists(history_file):
                        profile_name = os.path.basename(os.path.dirname(history_file))
                        self.get_chromium_history(history_file, f"{browser_name}_{profile_name}", username)
            
            webkit_browsers = [
                ('~/.local/share/epiphany/ephy-history.db', 'epiphany'),
                ('~/.config/midori/history.db', 'midori')
            ]
            
            for browser_path, browser_name in webkit_browsers:
                full_path = browser_path.replace('~', home_path)
                if os.path.exists(full_path):
                    self.get_webkit_history(full_path, browser_name, username)
            
            text_browsers = [
                ('~/.lynx_history', 'lynx'),
                ('~/.links/history', 'links'),
                ('~/.w3m/history', 'w3m')
            ]
            
            for browser_path, browser_name in text_browsers:
                full_path = browser_path.replace('~', home_path)
                if os.path.exists(full_path):
                    self.process_text_browser_history(full_path, browser_name, username)
        
        logging.info("Browser history collection completed")
    
    def process_text_browser_history(self, history_path, browser_name, username):
        try:
            with open(history_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            for line in lines[-100:]:  # Get last 100 records
                url = line.strip()
                if url and (url.startswith('http://') or url.startswith('https://')):
                    self.save_entry(current_time, url, browser_name, username)
                    
        except Exception as e:
            logging.error(f"Error processing text browser history {history_path}: {e}")

def main():
    collector = BrowserHistoryCollector()
    collector.collect_all_history()

if __name__ == "__main__":
    main()
