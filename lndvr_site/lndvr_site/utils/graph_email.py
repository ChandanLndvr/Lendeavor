from msal import ConfidentialClientApplication
import requests
from django.conf import settings
def send_graph_email(subject, body, to_emails, is_html=False, attachments=None):
    app = ConfidentialClientApplication(
        settings.MS_GRAPH_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MS_GRAPH_TENANT_ID}",
        client_credential=settings.MS_GRAPH_CLIENT_SECRET
    )
    token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" in token_response:
        access_token = token_response["access_token"]
        endpoint = f"https://graph.microsoft.com/v1.0/users/{settings.GRAPH_SENDER_EMAIL}/sendMail"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML" if is_html else "Text",
                    "content": body
                },
                "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_emails]
            },
            "saveToSentItems": "true"
        }

        # Attach files if provided
        if attachments:
            message["message"]["attachments"] = attachments

        response = requests.post(endpoint, headers=headers, json=message)
        print("Graph API Response:", response.status_code, response.text)

        if response.status_code in (200, 202):
            return True
        else:
            print(f"Failed to send email: {response.status_code} - {response.text}")
            return False
    else:
        print("Token acquisition failed:", token_response.get("error_description"))
        return False
