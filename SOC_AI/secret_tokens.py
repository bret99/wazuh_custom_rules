# OpenSearch connection settings
HOST = 'http://localhost:9200'# change if necessary
INDEX = 'wazuh-alerts*'
OS_USERNAME = '' # insert actual volume here
OS_PASSWORD = '' # insert actual volume here
SCROLL_TIMEOUT = '10m'  # Scroll timeout
BATCH_SIZE = 2000 # Pagination batch size
# ====== Events filtration ======
IGNORE_RULE_IDS = [""] # insert actual volumes here
IGNORE_RULE_GROUPS = [""] # insert actual volumes here
LOG_FILE = "/tmp/wazuh_events_level3_10.json" # change if necessary
# ====== VK TEAMS SETTINGS ======
VK_TEAMS_TOKEN = '' # insert actual volume here
VK_TEAMS_CHAT_ID = '' # insert actual volume here
VK_TEAMS_HOOK_URL = "https://myteam.mail.ru/bot/v1/messages/sendText"
# ====== EMAIL SETTINGS ======
SMTP_SERVER = '' # insert actual volume here
SMTP_PORT = 587 # 465 for SMTPS (SSL), 587 for STARTTLS
EMAIL_FROM = '' # insert actual volume here (email)
EMAIL_PASSWORD = '' # insert actual volume here
# ====== EMAIL RECIPIENTS ======
EMAIL_RECIPIENTS = [] # insert actual volumes here
# ====== AI MODEL SETTINGS ======
MODEL_NAME = "jackaduma/SecRoBERTa" # change if necessary
FALLBACK_MODEL = "distilroberta-base" # change if necessary
TOP_CRITICAL_EVENTS = 50
# Telegram Settings (add these if you want to use Telegram)
TELEGRAM_BOT_TOKEN = '' # insert actual volume here
TELEGRAM_CHAT_ID = '' # insert actual volume here
