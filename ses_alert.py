"""
AWS SES Alert Module for uptime_monitor.
Handles email alert formatting and dispatch via boto3 SES client with dry-run support.
"""

import os
import sys
import html
import datetime
import logging
from botocore.exceptions import ClientError, BotoCoreError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ses_alert")


def _safe_stdout_reconfigure():
    """Ensure sys.stdout uses UTF-8 encoding on platforms like Windows where default might be cp1252."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass


def _safe_print_dry_run(recipient, subject, body):
    """
    Safely log and print dry-run alert details without UnicodeEncodeError on Windows cp1252 consoles.
    """
    _safe_stdout_reconfigure()

    msg_log = f"[DRY_RUN] Email alert logged. Recipient: {recipient} | Subject: '{subject}' | Body: '{body.strip()}'"
    try:
        logger.info(msg_log)
    except Exception:
        pass

    msg_print = f"[DRY-RUN] SES Alert Payload: recipient={recipient}, subject={subject}, body={body}"
    try:
        print(msg_print)
    except UnicodeEncodeError:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout.buffer.write((msg_print + "\n").encode("utf-8", errors="replace"))
        else:
            encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
            safe_msg = msg_print.encode(encoding, errors="replace").decode(encoding)
            print(safe_msg)


def format_alert_email(url, status_code=None, details=""):
    """
    Formats the subject and body for an uptime failure alert email.

    Args:
        url (str): Target site URL.
        status_code (int or None): HTTP status code, if available.
        details (str): Additional details or error message.

    Returns:
        tuple: (subject, body)
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    status_str = str(status_code) if status_code is not None else "N/A"
    subject = f"ALERT: Site Down - {url} (HTTP {status_str})"
    
    body = (
        f"Uptime Monitoring Failure Alert\n"
        f"----------------------------------------\n"
        f"Target URL   : {url}\n"
        f"Status Code  : {status_str}\n"
        f"Timestamp    : {timestamp}\n"
        f"Failure Info : {details}\n"
        f"----------------------------------------\n"
        f"Automated notification from Uptime Monitor.\n"
    )
    return subject, body


def send_ses_alert(
    recipient="utkarshethics@gmail.com",
    subject="ALERT: Site Down",
    body="Target site is unreachable.",
    dry_run=False,
    aws_region=None,
):
    """
    Sends an email alert via AWS SES or logs payload in dry-run mode.

    Args:
        recipient (str): Destination email address.
        subject (str): Email subject.
        body (str): Email body text.
        dry_run (bool): If True, log alert payload without calling boto3 SES.
        aws_region (str or None): AWS region to use for SES client.

    Returns:
        bool or dict: True or response dict on success/dry-run, False on failure.
    """
    is_dry_run = (
        dry_run
        or os.getenv("DRY_RUN", "").lower() in ("true", "1", "yes")
        or os.getenv("MOCK_SES", "").lower() in ("true", "1", "yes")
    )

    if is_dry_run:
        _safe_print_dry_run(recipient, subject, body)
        return True

    region = (
        aws_region
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or "us-east-1"
    )

    try:
        import boto3
        ses_client = boto3.client("ses", region_name=region)
        escaped_body = html.escape(body)
        response = ses_client.send_email(
            Source=recipient,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body, "Charset": "UTF-8"},
                    "Html": {"Data": f"<html><body><pre>{escaped_body}</pre></body></html>", "Charset": "UTF-8"},
                },
            },
        )
        logger.info(f"SES alert successfully sent to {recipient}. MessageId: {response.get('MessageId')}")
        return response
    except (ClientError, BotoCoreError, Exception) as e:
        logger.error(f"Failed to send SES alert to {recipient}: {e}")
        return False


# Alias for backwards compatibility / module flexibility
send_alert = send_ses_alert
