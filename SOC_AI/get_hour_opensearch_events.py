#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from opensearchpy import OpenSearch, OpenSearchException
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Import configuration from access_tokens.py
try:
    from secret_tokens import HOST, INDEX, OS_USERNAME, OS_PASSWORD, SCROLL_TIMEOUT, BATCH_SIZE, IGNORE_RULE_IDS, IGNORE_RULE_GROUPS, LOG_FILE
except ImportError:
    print("Error: secret_tokens.py file not found or configuration missing")
    sys.exit(1)

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
        print(f"Filtered {filtered_count} events with exception rules")
    
    return filtered_events

def fetch_all_alerts_with_scroll(client):
    all_events = []
    scroll_id = None
    
    try:
        # Using timezone-aware datetime
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

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
                    "must_not": [
                        {"terms": {"rule.id": IGNORE_RULE_IDS}},
                        {"terms": {"rule.groups": IGNORE_RULE_GROUPS}}
                    ]
                }
            }
        }

        print(f"Starting events collecting using Scroll API...")
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
        
        print(f"Events found: {total_hits}")
        
        batch_events = [hit["_source"] for hit in hits]
        all_events.extend(batch_events)
        print(f"First part: {len(batch_events)} events (all: {len(all_events)})")
        
        # Getting other results
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
                print(f"Error with scroll: {e}")
                break
        
        print(f"Scroll API collected {len(all_events)} events")
        return all_events
        
    except Exception as e:
        print(f"Error with scroll request: {e}")
        return all_events
    finally:
        if scroll_id:
            try:
                client.clear_scroll(scroll_id=scroll_id)
                print("Scroll context cleaned")
            except:
                pass

def fetch_alerts_with_search_after(client):
    all_events = []
    last_sort = None
    
    try:
        # Using timezone-aware datetime
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)

        query = {
            "size": BATCH_SIZE,
            "sort": [
                {"@timestamp": {"order": "asc"}},
                {"_id": {"order": "asc"}}
            ],
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
                    "must_not": [
                        {"terms": {"rule.id": IGNORE_RULE_IDS}},
                        {"terms": {"rule.groups": IGNORE_RULE_GROUPS}}
                    ]
                }
            }
        }

        print("Using search_after to collect events...")
        print(f"Time range: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        has_more = True
        page = 1
        max_pages = 1000  # Endless cycle protect
        
        while has_more and page <= max_pages:
            try:
                if last_sort:
                    query["search_after"] = last_sort
                
                response = client.search(
                    index=INDEX, 
                    body=query, 
                    request_timeout=120
                )
                
                hits = response['hits']['hits']
                
                if not hits:
                    print(f"Search_after: no data anymore (page {page})")
                    has_more = False
                    break
                
                batch_events = [hit["_source"] for hit in hits]
                all_events.extend(batch_events)
                
                # Getting value of sort for the next page
                last_hit = hits[-1]
                last_sort = last_hit['sort']
                
                print(f"Search_after page {page}: {len(batch_events)} events (all: {len(all_events)})")
                page += 1
                
                # If got less than BATCH_SIZE than this is last page
                if len(hits) < BATCH_SIZE:
                    print(f"Search_after: last page got (less than {BATCH_SIZE} events)")
                    has_more = False
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error at page {page} search_after: {e}")
                has_more = False
        
        print(f"Search_after collected {len(all_events)} events")
        return all_events
        
    except Exception as e:
        print(f"General error search_after: {e}")
        return all_events

def save_events_log(events):
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        print(f"Events saved to file: {LOG_FILE}")
        file_size = os.path.getsize(LOG_FILE) / (1024 * 1024)
        print(f"File size: {file_size:.2f} MB")
        return True
    except Exception as e:
        print(f"Erro during file saving: {e}")
        return False

def main():
    print(f"Plugin at OpenSearch: {HOST}")

    try:
        client = get_opensearch_client()

        if not client.ping():
            print("Failed plugin at OpenSearch")
            return None

        print("Successful plugin at OpenSearch")

        # Using timezone-aware datetime for requests
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)
        
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        # Getting events UNTIL filtration
        count_query_before = {
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
                    ]
                }
            }
        }
        
        # Getting events AFTER filtration
        count_query_after = {
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
                    "must_not": [
                        {"terms": {"rule.id": IGNORE_RULE_IDS}},
                        {"terms": {"rule.groups": IGNORE_RULE_GROUPS}}
                    ]
                }
            }
        }
        
        try:
            count_before = client.count(index=INDEX, body=count_query_before)['count']
            count_after = client.count(index=INDEX, body=count_query_after)['count']
            
            print(f"Events amount until filtartion: {count_before}")
            print(f"Expected events amount after filtration: {count_after}")
            print(f"To be filtered: {count_before - count_after} events")
        except Exception as e:
            print(f"Events count error: {e}")
            count_after = 0

        if count_after == 0:
            print("No events after filtration done.")
            # Trying anyway to collect events using scroll
            print("Trying collecting data using Scroll API...")
            events = fetch_all_alerts_with_scroll(client)
        else:
            # Chosing method respectevely to events amount
            if count_after <= 10000:
                print("Usual search...")
                query = {
                    "size": min(count_after, 10000),  # Limit at size
                    "sort": [{"@timestamp": {"order": "desc"}}],
                    "query": count_query_after["query"]
                }
                response = client.search(index=INDEX, body=query, request_timeout=120)
                events = [hit["_source"] for hit in response['hits']['hits']]
            else:
                print(f"More than 10,000 events. Using Scroll API...")
                events = fetch_all_alerts_with_scroll(client)

        # Additional filtration
        events = filter_events(events)
        
        print(f"Events amount: {len(events)}")

        if not events:
            print("Events collection failed")
            return None

        if save_events_log(events):
            print(f"Successfully saved {len(events)} events at {LOG_FILE}")
            return LOG_FILE
        else:
            return None

    except Exception as e:
        print(f"Error in job with OpenSearch: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"Events collection ended successfully. File: {result}")
        sys.exit(0)
    else:
        print("Events collection ended with error or there is no data")
        sys.exit(1)
