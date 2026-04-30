"""Email sender placeholder for local demo."""


def send_email(to_email: str, subject: str, body: str) -> dict:
    return {'to': to_email, 'subject': subject, 'sent': True}
