from opensearchpy import OpenSearch
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import ssl
from secret_tokens import HOST, INDEX, OS_USERNAME, OS_PASSWORD, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SENDER, DOMAIN

# ====== BASE EMAIL TEXT ======
EMAIL_SUBJECT = 'Publication of restricted access information'
BASE_EMAIL_BODY = (
    'Hello!\n\n'
    'We draw your attention to the established fact of violation of the company\'s Information Security Policy: in {jira_task} placement of restricted access information on a non-corporate resource {jira_secret} in open access was detected, which poses a threat to the confidentiality and integrity of information assets of company.\n\n'
    'This is a direct violation of our information protection standards and entails serious consequences, including the possibility of information falling into the hands of third parties, damage to the Company\'s reputation, financial losses, and even legal liability.\n\n'
    'Risks associated with such action:\n\n'
    '1. **Possibility of illegal use of trade secrets by competitors**\n'
    '2. **Leakage of personal data of employees and clients**\n'
    '3. **Threat to the Company\'s financial stability due to disclosure of trade secrets**\n'
    '4. **Risk of unauthorized cross-border transfer of restricted access information, leading to additional legal consequences and sanctions from regulatory authorities**\n\n'
    'In connection with the above, we ask you to provide the following information:\n\n'
    '1. for what purpose you created and/or used the document in {jira_secret};\n'
    '2. within the framework of which job duties or management instructions you created and/or made changes to this file;\n'
    '3. reasons for using non-corporate cloud services;\n'
    '4. whether you have familiarized yourself with the Information Security Policy of company.\n\n'
    'We strongly recommend refraining from further violations of information processing and storage rules, and immediately ceasing any such actions. Please confirm receipt of this notification and take necessary measures to eliminate the violations (transfer information from non-corporate cloud resources to corporate cloud resources, delete the document in {jira_secret}).\n\n'
    'Consequences of non-compliance with these requirements will be considered by the management of company and may lead to disciplinary sanctions up to termination of employment contract.\n\n'
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
                                {"match_phrase": {"rule.id": "100104"}} # Change rule id if necessary
                            ],
                            "minimum_should_match": 1
                        }
                    },
                    {"range": {"@timestamp": {"gte": "now-30m/m", "lt": "now"}}} # Change time period if necessary
                ]
            }
        }
    }

    resp = client.search(index=INDEX, body=query)
    total = resp.get('hits', {}).get('total', {}).get('value', 0)
    if total == 0:
        print("No documents found for the last 30 minutes.")
        return {}

    user_info = {}
    for hit in resp.get('hits', {}).get('hits', []):
        try:
            source = hit["_source"]["data"]
            jira_creator = source["jira_creator"]
            jira_task = source.get("jira_task", "unknown")
            jira_secret = source.get("jira_secret", "unknown")

            if jira_creator and isinstance(jira_creator, str):
                # Normalize username
                u = jira_creator.strip()
                if "\\" in u:
                    u = u.split("\\", 1)[1]
                if u.endswith("$"):
                    continue
                if "@" in u:
                    u = u.split("@", 1)[0]

                if u not in user_info:
                    user_info[u] = {
                        'jira_task': jira_task,
                        'jira_secret': jira_secret
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
                jira_task=info['jira_task'],
                jira_secret=info['jira_secret']
            )
            send_email(email, EMAIL_SUBJECT, email_body)
            print(f"Sent: {email} (Task: {info['jira_task']}, secret: {info['jira_secret']})")
        except Exception as e:
            print(f"Sending error for {email}: {e}")

if __name__ == "__main__":
    main()
