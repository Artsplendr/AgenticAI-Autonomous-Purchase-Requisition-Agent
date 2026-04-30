"""Approval MCP client stub."""

from tools.email_sender import send_email
from tools.slack_notifier import send_slack_message


class ApprovalMCPClient:
    def send_approval_request(self, approver: str, amount: float) -> dict:
        send_slack_message('#procurement', f'Approval needed from {approver}: EUR {amount}')
        return send_email(approver, 'Approval Request', f'Please approve purchase of EUR {amount}.')
