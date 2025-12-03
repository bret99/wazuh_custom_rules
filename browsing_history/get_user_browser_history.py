from opensearchpy import OpenSearch
from datetime import datetime, timedelta
import json
import os
import warnings
from urllib3.exceptions import InsecureRequestWarning
from access_tokens import HOST, INDEX, OS_USERNAME, OS_PASSWORD

# Suppress SSL warnings
warnings.filterwarnings("ignore", category=InsecureRequestWarning)
warnings.filterwarnings("ignore", message="Connecting to.*using SSL with verify_certs=False is insecure")

# ====== FILE SETTINGS ======
REPORT_DIR = '/tmp'

def get_opensearch_client():
    """Create OpenSearch client with increased timeout"""
    return OpenSearch(
        hosts=[HOST],
        http_auth=(OS_USERNAME, OS_PASSWORD),
        use_ssl=True,
        verify_certs=False,
        timeout=60,
        max_retries=3,
        retry_on_timeout=True,
        ssl_show_warn=False
    )

def get_user_input():
    """Get interactive input from user"""
    print("\n" + "="*50)
    print("BROWSING HISTORY SEARCH CONFIGURATION")
    print("="*50)

    # User settings choose
    print("\nChoose search type:")
    print("1 - Search for specific user")
    print("2 - Search for ALL users")
    
    while True:
        try:
            search_type = input("\nYour choice (1-2): ").strip()
            if search_type in ['1', '2']:
                break
            print("Invalid choice. Please enter 1 or 2.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            exit(0)
    
    username = None
    search_all_users = False
    
    if search_type == '1':
        # Get username for specific user search
        while True:
            username = input("\nEnter username to search (url_user): ").strip()
            if username:
                break
            print("Username cannot be empty. Please try again.")
    else:
        # Search for all users
        search_all_users = True
        username = "ALL_USERS"
        print("\n⚠️  WARNING: Searching browsing history for ALL users.")
        print("This may return a large amount of data and take longer to process.")
        
        confirm = input("\nContinue with search for ALL users? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            exit(0)
    
    # Get search period
    print("\nChoose search period:")
    print("1 - Custom period (in days)")
    print("2 - Custom date range (YYYY-MM-DD to YYYY-MM-DD)")
    
    while True:
        try:
            choice = input("\nYour choice (1-2): ").strip()
            
            if choice == '1':
                try:
                    days = int(input("Enter number of days: "))
                    if days <= 0:
                        print("Number of days must be positive.")
                        continue
                    period_name = f"{days} days"
                    start_date_str, end_date_str = calculate_date_range(days)
                    break
                except ValueError:
                    print("Please enter a valid number.")
            elif choice == '2':
                try:
                    start_date_input = input("Enter start date (YYYY-MM-DD): ").strip()
                    end_date_input = input("Enter end date (YYYY-MM-DD): ").strip()
                    
                    # Validate date format
                    start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
                    end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
                    
                    if start_date > end_date:
                        print("Start date cannot be later than end date.")
                        continue
                    
                    if start_date > datetime.now():
                        print("Start date cannot be in the future.")
                        continue
                    
                    # Calculate days difference for display
                    days_diff = (end_date - start_date).days
                    if days_diff < 0:
                        print("Invalid date range.")
                        continue
                    
                    period_name = f"{start_date_input} to {end_date_input}"
                    start_date_str = start_date.isoformat()
                    end_date_str = end_date.replace(hour=23, minute=59, second=59).isoformat()
                    days = days_diff  # For statistics
                    break
                    
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD format.")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Invalid choice. Please enter a number from 1 to 2.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            exit(0)
    
    # Display search parameters
    print("\n" + "="*50)
    print("SEARCH PARAMETERS:")
    if search_all_users:
        print(f"  • Search type: ALL USERS")
    else:
        print(f"  • Username: {username}")
    print(f"  • Period: {period_name}")
    print(f"  • Start: {start_date_str[:10]}")
    print(f"  • End: {end_date_str[:10]}")
    print("="*50)
    
    confirm = input("\nStart search? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Operation cancelled.")
        exit(0)
    
    return username, start_date_str, end_date_str, days, period_name, search_all_users

def calculate_date_range(days):
    """Calculate date range based on number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for OpenSearch
    start_date_str = start_date.isoformat()
    end_date_str = end_date.isoformat()
    
    return start_date_str, end_date_str

def generate_report_filename(username, search_all_users):
    """Generate report filename with username and human-readable date"""
    # Format date in human-readable format
    readable_date = datetime.now().strftime("%d-%m-%Y_%H-%M")
    
    if search_all_users:
        filename = f"browsing_history_ALL_USERS_{readable_date}.json"
    else:
        # Sanitize username for filename
        safe_username = "".join(c for c in username if c.isalnum() or c in ('-', '_')).rstrip()
        if not safe_username:
            safe_username = "unknown_user"
        
        filename = f"browsing_history_{safe_username}_{readable_date}.json"
    
    return os.path.join(REPORT_DIR, filename)

def fetch_browsing_history(client, username, start_date, end_date, search_all_users):
    """Get browsing history for specified user(s) and period"""
    # Build query based on search type
    if search_all_users:
        # Query for all users - remove username filter
        query = {
            "size": 1000,  # Batch size for scroll
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {"match_phrase": {"rule.groups": "browsing_history"}}
                                ],
                                "minimum_should_match": 1
                            }
                        },
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": start_date,
                                    "lte": end_date
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc"
                    }
                }
            ]
        }
    else:
        # Query for specific user
        query = {
            "size": 1000,  # Batch size for scroll
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {"match_phrase": {"rule.groups": "browsing_history"}}
                                ],
                                "minimum_should_match": 1
                            }
                        },
                        {
                            "term": {"data.url_user": username}
                        },
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": start_date,
                                    "lte": end_date
                                }
                            }
                        }
                    ]
                }
            },
            "sort": [
                {
                    "@timestamp": {
                        "order": "desc"
                    }
                }
            ]
        }
    
    try:
        print("Executing search query...")
        # Initialize scroll
        resp = client.search(
            index=INDEX,
            body=query,
            scroll='5m'  # Scroll context lifetime
        )
        
        scroll_id = resp['_scroll_id']
        total = resp.get('hits', {}).get('total', {}).get('value', 0)
        
        if search_all_users:
            print(f"\nFound {total} browsing events for ALL users")
        else:
            print(f"\nFound {total} browsing events for user '{username}'")
        
        print(f"from {start_date[:10]} to {end_date[:10]}")
        
        if total == 0:
            print("\nNo documents found for the specified period.")
            return []

        # Collect all data via scroll
        browsing_data = []
        batch_count = 0
        
        while len(resp['hits']['hits']) > 0:
            batch_count += 1
            batch_size = len(resp['hits']['hits'])
            
            # Add data from current batch
            for hit in resp['hits']['hits']:
                source_data = hit["_source"]
                data_field = source_data.get('data', {})
                
                event_data = {
                    'timestamp': source_data.get('@timestamp', ''),
                    'url_user': data_field.get('url_user', ''),
                    'url_address': data_field.get('url_address', ''),
                    'url_time': data_field.get('url_time', ''),
                    'url_browser': data_field.get('url_browser', 'Unknown'),
                    'rule_description': source_data.get('rule', {}).get('description', '')
                }
                browsing_data.append(event_data)
            
            print(f"Processed batch {batch_count}: {batch_size} records, total: {len(browsing_data)}")
            
            # Get next batch
            try:
                resp = client.scroll(
                    scroll_id=scroll_id,
                    scroll='5m'
                )
                scroll_id = resp['_scroll_id']
            except Exception as e:
                print(f"Error getting next batch: {e}")
                break

        # Clear scroll context
        try:
            client.clear_scroll(scroll_id=scroll_id)
        except:
            pass
        
        if search_all_users:
            print(f"\nTotal collected: {len(browsing_data)} browsing history records for ALL users")
        else:
            print(f"\nTotal collected: {len(browsing_data)} browsing history records")
        
        return browsing_data

    except Exception as e:
        print(f"\nError querying OpenSearch: {e}")
        
        # Check if error is related to missing data
        if "search_phase_execution_exception" in str(e).lower():
            print("Possible reasons:")
            print("1. No data in index for the specified period")
            print("2. Index doesn't exist or is not accessible")
            print("3. Query syntax error")
        elif "timeout" in str(e).lower():
            print("Connection timeout. Try increasing timeout value or check OpenSearch server.")
        
        return []

def analyze_index_coverage(client, start_date, end_date):
    """Check if index has data for specified period with timeout handling"""
    print("\nChecking index data coverage...")
    
    check_query = {
        "size": 0,
        "query": {
            "range": {
                "@timestamp": {
                    "gte": start_date,
                    "lte": end_date
                }
            }
        }
    }
    
    try:
        resp = client.search(
            index=INDEX,
            body=check_query,
            request_timeout=30
        )
        
        total = resp.get('hits', {}).get('total', {}).get('value', 0)
        
        print(f"Documents in requested range: {total}")
        
        if total == 0:
            print(f"\n⚠️  WARNING: No documents found in index for the specified period.")
            print("Possible reasons:")
            print("1. Index doesn't have data for this time range")
            print("2. Date format mismatch")
            print("3. Index pattern doesn't match any indices")
            
            confirm = input("\nContinue search anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                return False
        
        return True
        
    except Exception as e:
        print(f"Warning during index check: {e}")
        print("Continuing search despite index check warning...")
        return True  # Continue despite check error

def save_browsing_report(username, start_date, end_date, period_name, browsing_data, search_all_users):
    """Save browsing history data to JSON file with required fields"""
    # Generate report filename with username and date
    report_file = generate_report_filename(username, search_all_users)

    formatted_events = []
    for event in browsing_data:
        formatted_event = {
            'timestamp': event.get('timestamp', ''),
            'url_user': event.get('url_user', ''),
            'url_address': event.get('url_address', ''),
            'url_time': event.get('url_time', ''),
            'url_browser': event.get('url_browser', 'Unknown'),
            'rule_description': event.get('rule_description', '')
        }
        formatted_events.append(formatted_event)
    
    report = {
        "report_generated_at": datetime.now().isoformat(),
        "search_parameters": {
            "search_type": "ALL_USERS" if search_all_users else "SPECIFIC_USER",
            "username": username if not search_all_users else "ALL_USERS",
            "start_date": start_date,
            "end_date": end_date,
            "period": period_name,
            "query_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        "statistics": {
            "total_events": len(browsing_data),
            "unique_users": len(set([event.get('url_user', '') for event in browsing_data if event.get('url_user')])),
            "period_days": (datetime.fromisoformat(end_date.replace('Z', '+00:00')) - 
                          datetime.fromisoformat(start_date.replace('Z', '+00:00'))).days
        },
        "events": formatted_events
    }
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Report saved to: {report_file}")
        return report_file
    except Exception as e:
        print(f"\nError saving report: {e}")
        return None

def display_summary(username, browsing_data, start_date, end_date, period_name, report_file=None, search_all_users=False):
    """Display search results summary"""
    print("\n" + "="*60)
    print("SEARCH RESULTS SUMMARY")
    print("="*60)
    if search_all_users:
        print(f"Search type: ALL USERS")
    else:
        print(f"Username: {username}")
    print(f"Period: {period_name}")
    print(f"Date range: {start_date[:10]} to {end_date[:10]}")
    print(f"Total events found: {len(browsing_data)}")
    if report_file:
        print(f"Report file: {report_file}")
    print("="*60)
    
    if browsing_data:
        # Group by browsers
        browsers = {}
        domains = {}
        users = {}
        
        for event in browsing_data:
            # Collect browser info
            browser_name = event.get('url_browser', 'Unknown')
            browsers[browser_name] = browsers.get(browser_name, 0) + 1
            
            # Collect user info (only for ALL_USERS search)
            if search_all_users:
                user_name = event.get('url_user', 'Unknown')
                if user_name:
                    users[user_name] = users.get(user_name, 0) + 1
            
            # Collect domain info
            url = event.get('url_address', '')
            if url:
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    if domain:
                        domains[domain] = domains.get(domain, 0) + 1
                except:
                    pass
        
        print("\n📊 BROWSER STATISTICS:")
        for browser, count in sorted(browsers.items(), key=lambda x: x[1], reverse=True):
            print(f"  {browser}: {count} events")
        
        # User statistics for ALL_USERS search
        if search_all_users and users:
            unique_users = len(users)
            print(f"\n👥 USER STATISTICS:")
            print(f"  Unique users found: {unique_users}")
            
            if unique_users <= 20:  # Show all users if not too many
                print("\n  User activity breakdown:")
                for user, count in sorted(users.items(), key=lambda x: x[1], reverse=True):
                    print(f"    {user}: {count} events")
            else:
                print("\n  Top-10 most active users:")
                top_users = sorted(users.items(), key=lambda x: x[1], reverse=True)[:10]
                for user, count in top_users:
                    print(f"    {user}: {count} events")
        
        if domains:
            if search_all_users:
                print("\n🌐 TOP-10 DOMAINS (across all users):")
            else:
                print("\n🌐 TOP-10 DOMAINS:")
            
            sorted_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:10]
            for domain, count in sorted_domains:
                print(f"  {domain}: {count} visits")
        
        # Show recent events
        print("\n⏰ LAST 5 EVENTS:")
        for i, event in enumerate(browsing_data[:5]):
            timestamp = event.get('timestamp', '')
            url = event.get('url_address', 'No URL')
            browser = event.get('url_browser', 'Unknown')
            
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pass
            
            print(f"\n  {i+1}. Time: {timestamp}")
            if search_all_users:
                user = event.get('url_user', 'Unknown')
                print(f"     User: {user}")
            print(f"     URL: {url[:100]}{'...' if len(url) > 100 else ''}")
            print(f"     Browser: {browser}")
    
    print("\n" + "="*60)

def main():
    # Get user input
    username, start_date, end_date, days, period_name, search_all_users = get_user_input()
    
    print("\n" + "="*50)
    print("CONNECTING TO OPENSEARCH...")
    print("="*50)
    
    # Connect to OpenSearch
    try:
        client = get_opensearch_client()
        print("✅ Connected to OpenSearch")
    except Exception as e:
        print(f"❌ Failed to connect to OpenSearch: {e}")
        print("\nPlease check:")
        print(f"1. Is OpenSearch running at {HOST}?")
        print("2. Are the credentials correct?")
        print("3. Is the network connection stable?")
        
        retry = input("\nTry again? (y/n): ").strip().lower()
        if retry == 'y':
            main()
        return
    
    # Check index data coverage
    if not analyze_index_coverage(client, start_date, end_date):
        print("\nSearch cancelled.")
        return
    
    # Get browsing history data
    print("\n" + "="*50)
    if search_all_users:
        print("SEARCHING BROWSING HISTORY FOR ALL USERS...")
    else:
        print("SEARCHING BROWSING HISTORY...")
    print("="*50)
    
    browsing_data = fetch_browsing_history(client, username, start_date, end_date, search_all_users)
    
    # Save report
    if browsing_data:
        report_file = save_browsing_report(username, start_date, end_date, period_name, browsing_data, search_all_users)
        # Display summary
        display_summary(username, browsing_data, start_date, end_date, period_name, report_file, search_all_users)
            
    else:
        print("\n" + "="*50)
        print("SEARCH RESULTS")
        print("="*50)
        print("No browsing history events found.")
        print("\nPossible reasons:")
        if not search_all_users:
            print("1. User didn't browse websites in specified period")
            print("2. Incorrect username")
        else:
            print("1. No users browsed websites in specified period")
        print("3. No data in index for specified period")
        print("4. Browsing history monitoring is not enabled")
        
        retry = input("\nPerform new search? (y/n): ").strip().lower()
        if retry == 'y':
            main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
