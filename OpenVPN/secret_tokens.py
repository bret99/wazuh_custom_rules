abuseipdb_token = "" # insert your AbuseIPDB API key here; 1000 requests per day, 30000 requests per month
ip2location_token = "" # insert your IP2location API key here; 30000 requests per month
# ====== OPENSEARCH SETTINGS ======
HOST = 'http://localhost:9200' # change if necessary
INDEX = 'wazuh-alerts*'
OS_USERNAME = '' # insert actual volume here
OS_PASSWORD = '' # insert actual volume here

# ====== EMAIL SETTINGS ======
SMTP_HOST = '' # insert actual volume here
SMTP_PORT = 587  # 465 for SMTPS (SSL), 587 for STARTTLS
SMTP_USER = '' # insert actual volume here (email)
SMTP_PASS = '' # insert actual volume here
SENDER = '' # insert actual volume here (email)
DOMAIN = '' # insert actual volume here
