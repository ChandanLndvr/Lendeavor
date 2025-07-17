from msal import ConfidentialClientApplication
import requests
from django.conf import settings

def send_graph_email(subject, body, to_emails):
    app = ConfidentialClientApplication(
        settings.MS_GRAPH_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MS_GRAPH_TENANT_ID}",
        client_credential=settings.MS_GRAPH_CLIENT_SECRET
    )
    token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    print("Token Response:", token_response)

    if "access_token" in token_response:
        access_token = token_response["access_token"]
        endpoint = "https://graph.microsoft.com/v1.0/users/{sender}/sendMail".format(
            sender=settings.GRAPH_SENDER_EMAIL
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [{"emailAddress": {"address": addr}} for addr in to_emails]
            }
        }
        response = requests.post(endpoint, headers=headers, json=message)
        print("Graph API Response:", response.status_code, response.text)
        if response.status_code in (202, 200):
            return True
        else:
            return False
    else:
        print("Token acquisition failed:", token_response.get("error_description"))
        return False
