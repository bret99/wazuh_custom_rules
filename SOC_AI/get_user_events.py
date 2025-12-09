#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta, timezone
from opensearchpy import OpenSearch, OpenSearchException
import warnings
from urllib3.exceptions import InsecureRequestWarning

# SSL warnings supress
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

SCROLL_TIMEOUT = '10m'
BATCH_SIZE = 2000

# Fields to search user
USERNAME_FIELDS = [
    "data.win.eventdata.subjectUserName",
    "data.win.eventdata.targetUserName",
    "data.src_user",
    "data.dst_user",
    "data.srcuser",
    "data.dstuser",
    "data.jira_creator",
    "data.confluence_creator",
    "data.gitlab_user",
    "data.gitlab_username",
    "data.un",
    "syscheck.uname_after"
]

def get_opensearch_client():
    return OpenSearch(
        hosts=[HOST],
        http_auth=(OS_USERNAME, OS_PASSWORD),
        use_ssl=True,
        verify_certs=False,
        timeout=300
    )

def should_ignore_event(event):
    try:
        rule_id = event.get('rule', {}).get('id')
        if rule_id in IGNORE_RULE_IDS:
            return True
        
        rule_groups = event.get('rule', {}).get('groups', [])
        if any(group in rule_groups for group in IGNORE_RULE_GROUPS):
            return True
            
        return False
        
    except Exception:
        return False

def filter_events(events):
    if not events:
        return []
    
    original_count = len(events)
    filtered_events = [event for event in events if not should_ignore_event(event)]
    filtered_count = original_count - len(filtered_events)
    
    if filtered_count > 0:
        print(f"Filtered {filtered_count} events due to exclusions rule")
    
    return filtered_events

def fetch_all_alerts_with_scroll(client, username, start_time, end_time, case_sensitive=False)
    all_events = []
    scroll_id = None
    
    try:
        should_conditions = build_username_query(username, case_sensitive)
        
        query = {
            "size": BATCH_SIZE,
            "sort": ["_doc"],
            "query": {
                "bool": {
                    "must": [
                        {"range": {"rule.level": {"gt": 2, "lt": 11}}},
                        {"range": {
                            "@timestamp": {
                                "gte": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                "lte": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                            }
                        }}
                    ],
                    "should": should_conditions,
                    "minimum_should_match": 1,
                    "must_not": [
                        {"terms": {"rule.id": IGNORE_RULE_IDS}},
                        {"terms": {"rule.groups": IGNORE_RULE_GROUPS}}
                    ]
                }
            }
        }

        print(f"Events collectiing using Scroll API...")
        print(f"User name: {username}")
        print(f"Period: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Registry sensity: {'Yes' if case_sensitive else 'No'}")
        print(f"Finding in fields: {', '.join(USERNAME_FIELDS)}")
        
        response = client.search(
            index=INDEX, 
            body=query, 
            scroll=SCROLL_TIMEOUT,
            request_timeout=300
        )
        
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']
        total_hits = response['hits']['total']['value']
        
        print(f"Events found: {total_hits}")
        
        batch_events = [hit["_source"] for hit in hits]
        all_events.extend(batch_events)
        print(f"First part: {len(batch_events)} events (all: {len(all_events)})")
        
        while len(hits) > 0:
            try:
                response = client.scroll(
                    scroll_id=scroll_id,
                    scroll=SCROLL_TIMEOUT
                )
                
                scroll_id = response['_scroll_id']
                hits = response['hits']['hits']
                
                if hits:
                    batch_events = [hit["_source"] for hit in hits]
                    all_events.extend(batch_events)
                    print(f"Got: {len(batch_events)} events (all: {len(all_events)})")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error when scroll: {e}")
                break
        
        print(f"Scroll API collected {len(all_events)} events")
        return all_events
        
    except Exception as e:
        print(f"Error during scroll request: {e}")
        return all_events
    finally:
        if scroll_id:
            try:
                client.clear_scroll(scroll_id=scroll_id)
                print("Scroll context cleaned")
            except:
                pass

def extract_username_from_event(event, username):
    result = {
        "found_in": [],
        "values": {}
    }
    
    for field in USERNAME_FIELDS:
        try:
            keys = field.split('.')
            current = event
 
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    current = None
                    break
            
            if current and str(current) == str(username):
                result["found_in"].append(field)
                result["values"][field] = current
                
        except Exception:
            continue
    
    return result

def enrich_event_with_username_info(event, username)
    username_info = extract_username_from_event(event, username)
 
    if not hasattr(event, 'metadata'):
        event['_username_search_info'] = {}
    
    event['_username_search_info'] = {
        "searched_username": username,
        "found_in_fields": username_info["found_in"],
        "field_values": username_info["values"],
        "search_timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    return event

def save_events_log(events, username, start_time, end_time):
    try:
        start_str = start_time.strftime("%Y%m%d_%H%M%S")
        end_str = end_time.strftime("%Y%m%d_%H%M%S")
        safe_username = username.replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_")
        
        log_file = f"/tmp/wazuh_events_user_{safe_username}_{start_str}_to_{end_str}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        
        print(f"Events saved to file: {log_file}")
        file_size = os.path.getsize(log_file) / (1024 * 1024)
        print(f"File size: {file_size:.2f} MB")
        
        return log_file
        
    except Exception as e:
        print(f"File saving error: {e}")
        return None

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Wazuh events collecting for concrete user for concrete period',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s john.doe 7
  %(prog)s "DOMAIN\\john.doe" 30
  %(prog)s administrator 1
  %(prog)s gitlab-user 14 --end-date 2024-01-31

Searchin in fields:
  • data.win.eventdata.subjectUserName
  • data.win.eventdata.targetUserName
  • data.src_user, data.dst_user
  • data.srcuser, data.dstuser
  • data.jira_creator, data.confluence_creator
  • data.gitlab_user, data.gitlab_username
  • data.un
  • syscheck.uname_after
        '''
    )
    
    parser.add_argument(
        'username',
        type=str,
        help='User name to search'
    )
    
    parser.add_argument(
        'days',
        type=int,
        help='Days amount to collect events (for example: 7 for the last 7 days)'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='End date in format YYYY-MM-DD (current time as default)'
    )
    
    parser.add_argument(
        '--case-sensitive',
        action='store_true',
        default=False,
        help='Registry sensity (case insensitive as default)'
    )
    
    return parser.parse_args()

def validate_arguments(args):
    if args.days <= 0:
        print("Error: days amount should be positive")
        sys.exit(1)
    
    if args.end_date:
        try:
            datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            print("Error: incorrect date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    return True

def build_username_query(username, case_sensitive=False):
    should_conditions = []
    
    if case_sensitive:
        for field in USERNAME_FIELDS:
            should_conditions.append({"term": {field: username}})
    else:
        for field in USERNAME_FIELDS:
            should_conditions.append({
                "match": {
                    field: {
                        "query": username,
                        "operator": "and",
                        "fuzziness": "0"
                    }
                }
            })
    
    return should_conditions

def main():
    args = parse_arguments()
    validate_arguments(args)
    
    username = args.username
    days = args.days
    case_sensitive = args.case_sensitive
    
    if args.end_date:
        end_time = datetime.strptime(args.end_date, "%Y-%m-%d")
        end_time = end_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        end_time = end_time.replace(tzinfo=timezone.utc)
    else:
        end_time = datetime.now(timezone.utc)
    
    start_time = end_time - timedelta(days=days)
    
    print(f"Events collecting for user: {username}")
    print(f"Registry sensity: {'Yes' if case_sensitive else 'No'}")
    print(f"Period: {days} day(days)")
    print(f"Reriod start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Period end: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Search in fields: {', '.join(USERNAME_FIELDS)}")
    
    start_str = start_time.strftime("%Y%m%d_%H%M%S")
    end_str = end_time.strftime("%Y%m%d_%H%M%S")
    safe_username = username.replace(" ", "_").replace("/", "_").replace("\\", "_").replace(":", "_")
    LOG_FILE = f"/tmp/wazuh_events_user_{safe_username}_{start_str}_to_{end_str}.json"
    
    print(f"Connect to OpenSearch: {HOST}")

    try:
        client = get_opensearch_client()

        if not client.ping():
            print("Failed connection to OpenSearch")
            return None

        print("Successful connection to OpenSearch")

        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        username_conditions = build_username_query(username, case_sensitive)
        
        count_query = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"rule.level": {"gt": 2, "lt": 11}}},
                        {"range": {
                            "@timestamp": {
                                "gte": start_time_str,
                                "lte": end_time_str
                            }
                        }}
                    ],
                    "should": username_conditions,
                    "minimum_should_match": 1,
                    "must_not": [
                        {"terms": {"rule.id": IGNORE_RULE_IDS}},
                        {"terms": {"rule.groups": IGNORE_RULE_GROUPS}}
                    ]
                }
            }
        }
        
        try:
            count_result = client.count(index=INDEX, body=count_query)['count']
            print(f"Events found: {count_result}")
            
            if count_result == 0:
                print("No events for chosen user for chosen period.")
                save_events_log([], username, start_time, end_time)
                return LOG_FILE
                
        except Exception as e:
            print(f"Events counting error: {e}")
            count_result = 0
          
        if count_result <= 10000:
            print(f"Standard search (events <= 10000)...")
            query = {
                "size": min(count_result, 10000),
                "sort": [{"@timestamp": {"order": "asc"}}],
                "query": count_query["query"]
            }
            response = client.search(index=INDEX, body=query, request_timeout=120)
            events = [hit["_source"] for hit in response['hits']['hits']]
        else:
            print(f"Events more 10,000, using Scroll API...")
            events = fetch_all_alerts_with_scroll(client, username, start_time, end_time, case_sensitive)

        print("Founf events processing...")
        processed_events = []
        for event in events:
            enriched_event = enrich_event_with_username_info(event, username)
            processed_events.append(enriched_event)
        
        processed_events = filter_events(processed_events)
        
        print(f"Итоговое количество собранных событий: {len(processed_events)}")

        if not processed_events:
            print("Failed to collect events")
            save_events_log([], username, start_time, end_time)
            return LOG_FILE

        if save_events_log(processed_events, username, start_time, end_time):
            print(f"Successfully saved {len(processed_events)} events")
            return LOG_FILE
        else:
            return None

    except Exception as e:
        print(f"Error during processing with OpenSearch: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"Events collecting successful. File: {result}")
        sys.exit(0)
    else:
        print("Events collecting ende with error")
        sys.exit(1)
