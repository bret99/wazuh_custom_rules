# OpenSearch connection settings
HOST = 'http://localhost:9200'# change if necessary
INDEX = 'wazuh-alerts*'
OS_USERNAME = '' # insert actual volume here
OS_PASSWORD = '' # insert actual volume here
SCROLL_TIMEOUT = '10m'  # Scroll timeout
BATCH_SIZE = 2000 # Pagination batch size
LOG_FILE = "/tmp/wazuh_events_level3_10.json"
