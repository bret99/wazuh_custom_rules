#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import time
from datetime import datetime, timedelta
from opensearchpy import OpenSearch, OpenSearchException

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
        timeout=300  # Timeout increasing for big requests
    )

def should_ignore_event(event):
    """
    Check if event should be ignored
    """
    try:
        # Check rule id
        rule_id = event.get('rule', {}).get('id')
        if rule_id in IGNORE_RULE_IDS:
            return True
        
        # Check rule groups
        rule_groups = event.get('rule', {}).get('groups', [])
        if any(group in rule_groups for group in IGNORE_RULE_GROUPS):
            return True
            
        return False
        
    except Exception:
        return False

def filter_events(events):
    """
    Filter events according to settings
    """
    if not events:
        return []
    
    original_count = len(events)
    filtered_events = [event for event in events if not should_ignore_event(event)]
    filtered_count = original_count - len(filtered_events)
    
    if filtered_count > 0:
        print(f"Filtered {filtered_count} events by exclusion rules")
    
    return filtered_events

def fetch_all_alerts_with_scroll(client):
    """
    Get ALL events using scroll API
    """
    all_events = []
    scroll_id = None
    
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)

        # Base query with filtering
        query = {
            "size": BATCH_SIZE,
            "sort": ["_doc"],  # Using _doc for efficiency
            "query": {
                "bool": {
                    "must": [
                        {"range": {"rule.level": {"gt": 2, "lt": 11}}}, # Change rule levels if necessary
                        {"range": {
                            "@timestamp": {
                                "gte": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "lte": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "format": "strict_date_optional_time"
                            }
                        }}
                    ],
                    "must_not": [
                        # Exclude rule ids
                        {"terms": {"rule.id": IGNORE_RULE_IDS}},
                        # Exclude rule groups
                        {"terms": {"rule.groups": IGNORE_RULE_GROUPS}}
                    ]
                }
            }
        }

        print(f"Starting collection of all events via Scroll API...")
        print(f"Ignoring rule ids: {IGNORE_RULE_IDS}")
        print(f"Ignoring rule groups: {IGNORE_RULE_GROUPS}")
        
        # First request
        response = client.search(
            index=INDEX, 
            body=query, 
            scroll=SCROLL_TIMEOUT,
            request_timeout=300
        )
        
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']
        total_hits = response['hits']['total']['value']
        
        print(f"Total events found (after filtering): {total_hits}")
        
        # Process first batch
        batch_events = [hit["_source"] for hit in hits]
        all_events.extend(batch_events)
        print(f"Received: {len(batch_events)} events (total: {len(all_events)})")
        
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
                    print(f"Received more: {len(batch_events)} events (total: {len(all_events)})")
                
                # Pause to avoid overloading the server
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error during scroll: {e}")
                break
        
        return all_events
        
    except Exception as e:
        print(f"Error executing scroll request: {e}")
        return all_events
    finally:
        # Always clear scroll
        if scroll_id:
            try:
                client.clear_scroll(scroll_id=scroll_id)
                print("Scroll context cleared")
            except:
                pass

def fetch_alerts_with_search_after(client):
    """
    Alternative method with search_after for very large volumes
    """
    all_events = []
    last_sort = None
    
    try:
        end_time = datetime.utcnow()
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
                                "gte": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                                "lte": end_time.strftime("%Y-%m-%dT%H:%M:%S")
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

        print("Using search_after for event collection...")
        print(f"Ignoring rule ids: {IGNORE_RULE_IDS}")
        print(f"Ignoring rule groups: {IGNORE_RULE_GROUPS}")
        
        has_more = True
        page = 1
        
        while has_more:
            if last_sort:
                query["search_after"] = last_sort
            
            response = client.search(
                index=INDEX, 
                body=query, 
                request_timeout=120
            )
            
            hits = response['hits']['hits']
            
            if not hits:
                has_more = False
                break
            
            batch_events = [hit["_source"] for hit in hits]
            all_events.extend(batch_events)
            
            # Get sort value for next page
            last_hit = hits[-1]
            last_sort = last_hit['sort']
            
            print(f"Page {page}: received {len(batch_events)} events (total: {len(all_events)})")
            page += 1
            
            time.sleep(0.1)
        
        return all_events
        
    except Exception as e:
        print(f"Error during search_after: {e}")
        return all_events

def save_events_log(events):
    try:
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        print(f"Events saved to file: {LOG_FILE}")
        file_size = os.path.getsize(LOG_FILE) / (1024 * 1024)  # Size in MB
        print(f"File size: {file_size:.2f} MB")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

def main():
    print(f"Connecting to OpenSearch: {HOST}")

    try:
        client = get_opensearch_client()

        if not client.ping():
            print("Failed to connect to OpenSearch")
            return None

        print("Successfully connected to OpenSearch")

        # Get total event count BEFORE filtering
        count_query_before = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"rule.level": {"gt": 2, "lt": 11}}},
                        {"range": {"@timestamp": {"gte": "now-1h/h", "lte": "now"}}}
                    ]
                }
            }
        }
        
        # Get total event count AFTER filtering
        count_query_after = {
            "query": {
                "bool": {
                    "must": [
                        {"range": {"rule.level": {"gt": 2, "lt": 11}}},
                        {"range": {"@timestamp": {"gte": "now-1h/h", "lte": "now"}}}
                    ],
                    "must_not": [
                        {"terms": {"rule.id": IGNORE_RULE_IDS}},
                        {"terms": {"rule.groups": IGNORE_RULE_GROUPS}}
                    ]
                }
            }
        }
        
        count_before = client.count(index=INDEX, body=count_query_before)['count']
        count_after = client.count(index=INDEX, body=count_query_after)['count']
        
        print(f"Total events before filtering: {count_before}")
        print(f"Expected count after filtering: {count_after}")
        print(f"Will be filtered: {count_before - count_after} events")

        if count_after == 0:
            print("No events remaining after filtering.")
            return None

        # Select method based on quantity
        if count_after <= 10000:
            print("Using regular search...")
            query = {
                "size": count_after,
                "sort": [{"@timestamp": {"order": "desc"}}],
                "query": count_query_after["query"]
            }
            response = client.search(index=INDEX, body=query, request_timeout=120)
            events = [hit["_source"] for hit in response['hits']['hits']]
        else:
            print(f"More than 10,000 events, using Scroll API...")
            events = fetch_all_alerts_with_scroll(client)
            
            # If scroll didn't work, try search_after
            if len(events) < count_after and count_after > 10000:
                print("Scroll didn't return all events, trying search_after...")
                events = fetch_alerts_with_search_after(client)

        # Additional filtering in case OpenSearch missed something
        events = filter_events(events)
        
        print(f"Final count of collected events: {len(events)}")

        if not events:
            print("Failed to collect events after filtering")
            return None

        if save_events_log(events):
            print(f"Successfully saved {len(events)} events to {LOG_FILE}")
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
        print("Event collection completed with error or no data")
        sys.exit(1)
