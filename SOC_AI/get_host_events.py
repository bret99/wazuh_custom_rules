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
from secret_tokens import HOST, INDEX, OS_USERNAME, OS_PASSWORD, IGNORE_RULE_IDS, IGNORE_RULE_GROPS, SCROLL_TIMEOUT, BATCH_SIZE

# Suppress SSL warnings
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

def get_opensearch_client():
    return OpenSearch(
        hosts=[HOST],
        http_auth=(OS_USERNAME, OS_PASSWORD),
        use_ssl=True,
        verify_certs=False,
        timeout=300
    )

def should_ignore_event(event):
    """
    Checks if event should be ignored
    """
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
    """
    Filters events according to settings
    """
    if not events:
        return []
    
    original_count = len(events)
    filtered_events = [event for event in events if not should_ignore_event(event)]
    filtered_count = original_count - len(filtered_events)
    
    if filtered_count > 0:
        print(f"Filtered {filtered_count} events by exclusion rules")
    
    return filtered_events

def fetch_all_alerts_with_scroll(client, agent_name, start_time, end_time):
    """
    Get ALL events using scroll API
    """
    all_events = []
    scroll_id = None
    
    try:
        query = {
            "size": BATCH_SIZE,
            "sort": ["_doc"],
            "query": {
                "bool": {
                    "must": [
                        {"term": {"agent.name": agent_name}},
                        {"range": {"rule.level": {"gt": 2, "lt": 16}}},
                        {"range": {
                            "@timestamp": {
                                "gte": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                                "lte": end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                            }
                        }}
                    ],
                    "must_not": [
                        {"terms": {"rule.id": IGNORE_RULE_IDS}},
                        {"terms": {"rule.groups": IGNORE_RULE_GROUPS}}
                    ]
                }
            }
        }

        print(f"Starting event collection via Scroll API...")
        print(f"Agent: {agent_name}")
        print(f"Time range: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        response = client.search(
            index=INDEX, 
            body=query, 
            scroll=SCROLL_TIMEOUT,
            request_timeout=300
        )
        
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']
        total_hits = response['hits']['total']['value']
        
        print(f"Total events found: {total_hits}")
        
        batch_events = [hit["_source"] for hit in hits]
        all_events.extend(batch_events)
        print(f"First batch: {len(batch_events)} events (total: {len(all_events)})")
        
        # Get remaining results
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
                    print(f"Received: {len(batch_events)} events (total: {len(all_events)})")
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error during scroll: {e}")
                break
        
        print(f"Scroll API collected {len(all_events)} events")
        return all_events
        
    except Exception as e:
        print(f"Error executing scroll query: {e}")
        return all_events
    finally:
        if scroll_id:
            try:
                client.clear_scroll(scroll_id=scroll_id)
                print("Scroll context cleared")
            except:
                pass

def save_events_log(events, agent_name, start_time, end_time):
    """
    Saves events to file with name containing agent and time range info
    """
    try:
        # Create filename based on parameters
        start_str = start_time.strftime("%Y%m%d_%H%M%S")
        end_str = end_time.strftime("%Y%m%d_%H%M%S")
        safe_agent_name = agent_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
        
        log_file = f"/tmp/wazuh_events_{safe_agent_name}_{start_str}_to_{end_str}.json"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        
        print(f"Events saved to file: {log_file}")
        file_size = os.path.getsize(log_file) / (1024 * 1024)
        print(f"File size: {file_size:.2f} MB")
        
        return log_file
        
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def parse_arguments():
    """
    Command line arguments parsing
    """
    parser = argparse.ArgumentParser(
        description='Collect Wazuh events for specific host for specified period',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Usage examples:
  %(prog)s agent1.example.com 7
  %(prog)s "Host Name With Spaces" 30
  %(prog)s DESKTOP-ABC123 1
        '''
    )
    
    parser.add_argument(
        'agent_name',
        type=str,
        help='Wazuh agent name (e.g., "agent1.example.com" or "DESKTOP-ABC123")'
    )
    
    parser.add_argument(
        'days',
        type=int,
        help='Number of days to collect events (e.g., 7 for last 7 days)'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='End date in YYYY-MM-DD format (default: current time)'
    )
    
    return parser.parse_args()

def validate_arguments(args):
    """
    Arguments validation
    """
    if args.days <= 0:
        print("Error: number of days must be positive")
        sys.exit(1)
    
    if args.end_date:
        try:
            datetime.strptime(args.end_date, "%Y-%m-%d")
        except ValueError:
            print("Error: invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    return True

def main():
    # Parse arguments
    args = parse_arguments()
    validate_arguments(args)
    
    agent_name = args.agent_name
    days = args.days
    
    # Define time range
    if args.end_date:
        end_time = datetime.strptime(args.end_date, "%Y-%m-%d")
        end_time = end_time.replace(hour=23, minute=59, second=59, microsecond=999999)
        end_time = end_time.replace(tzinfo=timezone.utc)
    else:
        end_time = datetime.now(timezone.utc)
    
    start_time = end_time - timedelta(days=days)
    
    print(f"Collecting events for agent: {agent_name}")
    print(f"Period: {days} day(s)")
    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Form log filename for display
    start_str = start_time.strftime("%Y%m%d_%H%M%S")
    end_str = end_time.strftime("%Y%m%d_%H%M%S")
    safe_agent_name = agent_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    LOG_FILE = f"/tmp/wazuh_events_{safe_agent_name}_{start_str}_to_{end_str}.json"
    
    print(f"Connecting to OpenSearch: {HOST}")

    try:
        client = get_opensearch_client()

        if not client.ping():
            print("Failed to connect to OpenSearch")
            return None

        print("Successfully connected to OpenSearch")

        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Get total events count
        count_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"agent.name": agent_name}},
                        {"range": {"rule.level": {"gt": 2, "lt": 16}}},
                        {"range": {
                            "@timestamp": {
                                "gte": start_time_str,
                                "lte": end_time_str
                            }
                        }}
                    ],
                    "must_not": [
                        {"terms": {"rule.id": IGNORE_RULE_IDS}},
                        {"terms": {"rule.groups": IGNORE_RULE_GROUPS}}
                    ]
                }
            }
        }
        
        try:
            count_result = client.count(index=INDEX, body=count_query)['count']
            print(f"Total events found: {count_result}")
            
            if count_result == 0:
                print("No events found for specified parameters.")
                save_events_log([], agent_name, start_time, end_time)
                return LOG_FILE
                
        except Exception as e:
            print(f"Error counting events: {e}")
            count_result = 0

        # Collect events
        if count_result <= 10000:
            print(f"Using standard search (events <= 10000)...")
            query = {
                "size": min(count_result, 10000),
                "sort": [{"@timestamp": {"order": "asc"}}],
                "query": count_query["query"]
            }
            response = client.search(index=INDEX, body=query, request_timeout=120)
            events = [hit["_source"] for hit in response['hits']['hits']]
        else:
            print(f"More than 10,000 events, using Scroll API...")
            events = fetch_all_alerts_with_scroll(client, agent_name, start_time, end_time)

        # Additional filtering
        events = filter_events(events)
        
        print(f"Final collected events count: {len(events)}")

        if not events:
            print("Failed to collect events")
            save_events_log([], agent_name, start_time, end_time)
            return LOG_FILE

        if save_events_log(events, agent_name, start_time, end_time):
            print(f"Successfully saved {len(events)} events")
            return LOG_FILE
        else:
            return None

    except Exception as e:
        print(f"Error working with OpenSearch: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"Event collection completed successfully. File: {result}")
        sys.exit(0)
    else:
        print("Event collection completed with error")
        sys.exit(1)
