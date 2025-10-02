from opensearchpy import OpenSearch
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import ssl
from secret_tokens import HOST, INDEX, OS_USERNAME, OS_PASSWORD, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SENDER, DOMAIN

# ====== BASE EMAIL TEXT ======
EMAIL_SUBJECT = 'Connection from abroad or hosting'
BASE_EMAIL_BODY = (
    'Hello!\n\n'
    'We hereby notify you that the monitoring systems of company have recorded access with your account to corporate resources from foreign IP addresses. This violates the internal policy, which allows access only from the territory of the Russian Federation and using corporate computing means.\n\n'
    'Security incident:\n\n'
    'OpenVPN: foreign or hosting connection of user {src_user} from address {srcip} from {country_name}.\n\n'
    'We remind you of the importance of complying with the following:\n\n'
    '1. **Prohibition of remote work outside the country**: Use of systems is possible only from the territory of the country, which is due to currency control requirements and personal data protection.\n'
    '2. **Employment contract**: Your employment contract implies that your workplace must be located on the territory of the country.\n'
    '3. **Information security policy**: It is prohibited to simultaneously use corporate and personal VPNs to access information. This may lead to data leakage.\n'
    '4. **Legislation**: Cross-border transfer of personal data and commercial secrets may entail legal liability in accordance with Federal Laws.\n\n'
    'In connection with the above, we ask you to provide the following information within 2 hours:\n\n'
    '1. Your location for the last 7 calendar days (country, city);\n'
    '2. dates and times of your connections to the Company\'s networks/resources;\n'
    '3. your use of non-corporate VPNs and equipment for access;\n'
    '4. whether your account was compromised (suspicions of compromise).\n\n'
    'If information is not received within two (2) hours, your account [Your login] will be temporarily blocked until the circumstances are clarified. If the compromise hypothesis is confirmed, the incident will be transferred to the security service for further consideration.\n\n'
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
                                {"match_phrase": {"rule.groups": "openvpn_foreign"}} # Change time period if necessary 
                            ],
                            "minimum_should_match": 1
                        }
                    },
                    {"range": {"@timestamp": {"gte": "now-10m/m", "lt": "now"}}} # Change time period if necessary 
                ]
            }
        }
    }

    resp = client.search(index=INDEX, body=query)
    total = resp.get('hits', {}).get('total', {}).get('value', 0)
    if total == 0:
        print("No documents found for the last 10 minutes.")
        return {}

    user_info = {}
    for hit in resp.get('hits', {}).get('hits', []):
        try:
            source = hit["_source"]["data"]
            src_user = source["src_user"]
            srcip = source.get("srcip", "unknown")
            country_name = source.get("abuesIPDB.countryName", "unknown")

            if src_user and isinstance(src_user, str):
                # Normalize username
                u = src_user.strip()
                if "\\" in u:
                    u = u.split("\\", 1)[1]
                if u.endswith("$"):
                    continue
                if "@" in u:
                    u = u.split("@", 1)[0]

                if u not in user_info:
                    user_info[u] = {
                        'srcip': srcip,
                        'country_name': country_name
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
                srcip=info['srcip'],
                country_name=info['country_name']
            )
            send_email(email, EMAIL_SUBJECT, email_body)
            print(f"Sent: {email} (Connection IP: {info['srcip']}, country: {info['country_name']})")
        except Exception as e:
            print(f"Sending error for {email}: {e}")

if __name__ == "__main__":
    main()
