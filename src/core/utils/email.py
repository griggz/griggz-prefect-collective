from typing import List, Literal, Optional

from clients.microsoft_ import MicrosoftClient


def send_email(
    recipients: List[str],
    subject: str,
    content: str,
    sender: str,
    content_type: Literal["HTML", "Text"],
) -> Optional[bool]:
    """
    Sends an email to specified recipients.

    Args:
    - recipients (List[str]): List of email addresses.
    - subject (str): Subject of the email.
    - content (str): HTML content of the email.

    Returns:
    - Optional[bool]: True if email sent successfully, else None.
    """
    try:
        email_client = MicrosoftClient()

        # Assuming the send_email method of MicrosoftClient returns a boolean
        success = email_client.send_email_(
            recipients=recipients,
            subject=subject,
            content=content,
            sender=sender,
            content_type=content_type,
        )
        return success
    except Exception as exc:
        print(f"Error sending email: {exc}")
        return None
