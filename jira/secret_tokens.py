jira_address = "" # insert your Jira address; example: https://jira.example.com
access_token_pass = "DOMAIN_USER_PASSWORD"
access_token_login = "DOMAIN_USERNAME"
secret_tokens = ["api_key", "access_token", "password", "docs.google.com", "drive.google.com", "access_key", "secret_key"] # configure as one like
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
