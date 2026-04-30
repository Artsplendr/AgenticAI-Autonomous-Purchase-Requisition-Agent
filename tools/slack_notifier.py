"""Slack notifier placeholder for local demo."""


def send_slack_message(channel: str, text: str) -> dict:
    return {'channel': channel, 'message': text, 'sent': True}
