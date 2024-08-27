import json
import os
from typing import List

import requests
from msal import ConfidentialClientApplication


class MicrosoftClient:
    def __init__(self):
        self.client_id = os.getenv("MICROSOFT_CLIENT_ID")
        self.client_secret = os.getenv("MICROSOFT_CLIENT_SECRECT_VALUE")
        self.tenant_id = os.getenv("MICROSOFT_TENANT_ID")
        self.token = None
        self.authority = (
            f"https://login.microsoftonline.com/{os.getenv('MICROSOFT_TENANT_ID')}"
        )
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.authenticate()

    def authenticate(self):
        app = ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )
        token_response = app.acquire_token_for_client(scopes=self.scopes)
        self.token = token_response.get("access_token")
        if not self.token:
            raise Exception("Authentication failed. Check your credentials.")

    def send_email_(
        self,
        recipients: List[str],
        subject: str,
        content: str,
        content_type: str = "Text",
        sender: str = "",
    ) -> None:
        if not self.token:
            print("Authenticating...")
            self.authenticate()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"

        to_recipients = [
            {"emailAddress": {"address": recipient}} for recipient in recipients
        ]

        email_message = None

        email_message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": content_type,
                    "content": content,
                },
                "toRecipients": to_recipients,
            },
            "saveToSentItems": "true",
        }

        response = requests.post(url, headers=headers, data=json.dumps(email_message))

        if response.status_code == 202:
            email_accounts = ", ".join(recipients)
            print(f"Email sent to {email_accounts} successfully.")
        else:
            print(
                f"Failed to send email to {email_accounts}. Status code: {response.status_code}, Response: {response.text}"
            )
