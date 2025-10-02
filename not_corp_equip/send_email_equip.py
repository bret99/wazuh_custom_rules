from opensearchpy import OpenSearch
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import ssl
from secret_tokens import HOST, INDEX, OS_USERNAME, OS_PASSWORD, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SENDER, DOMAIN

# ====== BASE EMAIL TEXT ======
EMAIL_SUBJECT = 'Connection from non-corporate equipment'
BASE_EMAIL_BODY = (
    'Hello!\n\n'
    'We hereby notify you that monitoring systems have recorded access with your account to corporate resources using non-corporate equipment.\n\n'
    'Connection details:\n'
    '- Device: {workstation_name}\n'
    '- IP address: {ip_address}\n\n'
    'We inform you that the use of non-corporate equipment to connect to the corporate information system is unacceptable in accordance with the Information Security Policy. This is due to a number of data security risks, as well as violation of legal requirements.\n'
    'The main risks when using personal devices are:\n'
    '1. **Vulnerability to cyber attacks and viruses, which can lead to leakage of confidential information.\n'
    '2. **Possibility of data interception by third parties through unsecured Wi-Fi networks.\n'
    '3. **Risk of device loss, which may result in loss of important corporate information\n'
    '4. **Inability to identify the legitimacy of the connection.\n\n'
    'We ask you to strictly comply with information security rules and use only corporate equipment for working with company data. If you need to use personal devices for temporary tasks, please coordinate such actions with the information security department.\n\n'
    'Violation of corporate resource usage rules entails disciplinary liability according to labor legislation, as well as administrative liability in accordance with the law on personal data.\n\n'
    'Explain the reason for connecting from non-corporate equipment.'
    'To record the fact of receiving this letter and your actions to correct the situation, please indicate in the response the list of all correspondence participants and explain the reason for the violation.\n\n'
    'Thank you in advance for your understanding and cooperation.\n\n'
    'Best regards,\n'
    'Information Security Department\n'
)

def get_opensearch_client():
    return OpenSearch(
        hosts=[HOST],
        http_auth=(OS_USERNAME, OS_PASSWORD),
        use_ssl=True,
        verify_certs=False  # set to True if you have valid certificates
    )

def fetch_user_info(client):
    # Query for the last 5 minutes
    query = {
        "size": 10000,
        "sort": [{"@timestamp": {"order": "desc"}}],
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": [
                                {"match_phrase": {"rule.groups": "equip_vpn"}},
                                {"match_phrase": {"rule.groups": "equip_domain"}}
                            ],
                            "minimum_should_match": 1
                        }
                    },
                    {"range": {"@timestamp": {"gte": "now-5m/m", "lt": "now"}}} # Change time period if necessary
                ]
            }
        }
    }

    resp = client.search(index=INDEX, body=query)
    total = resp.get('hits', {}).get('total', {}).get('value', 0)
    if total == 0:
        print("No documents found for the last 5 minutes.")
        return {}

    user_info = {}
    for hit in resp.get('hits', {}).get('hits', []):
        try:
            source = hit["_source"]["data"]["win"]["eventdata"]
            username_win = source["targetUserName"]
            workstation_name = source.get("workstationName", "unknown")
            ip_address = source.get("ipAddress", source.get("win.eventdata.ipAddress", "unknown"))

            if username_win and isinstance(username_win, str):
                # Normalize username
                u = username_win.strip()
                if "\\" in u:
                    u = u.split("\\", 1)[1]
                if u.endswith("$"):
                    continue
                if "@" in u:
                    u = u.split("@", 1)[0]
                
                if u not in user_info:
                    user_info[u] = {
                        'workstation_name': workstation_name,
                        'ip_address': ip_address
                    }
        except KeyError:
            continue
    
    return user_info

def send_email(recipient_email, subject, body):
    msg = MIMEText(body, _charset='utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = SENDER
    msg['To'] = recipient_email

    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SENDER, [recipient_email], msg.as_string())

def main():
    client = get_opensearch_client()
    user_info = fetch_user_info(client)
    if not user_info:
        return

    for username, info in sorted(user_info.items()):
        email = f"{username}@{DOMAIN}"
        try:
            # Form email body with specific connection data
            email_body = BASE_EMAIL_BODY.format(
                workstation_name=info['workstation_name'],
                ip_address=info['ip_address']
            )
            send_email(email, EMAIL_SUBJECT, email_body)
            print(f"Sent: {email} (Device: {info['workstation_name']}, IP: {info['ip_address']})")
        except Exception as e:
            print(f"Sending error for {email}: {e}")

if __name__ == "__main__":
    main()
