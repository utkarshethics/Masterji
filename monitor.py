"""
Main Uptime Monitor script for checking site availability and sending SES alerts.
Supports CLI arguments, environment variable overrides, retry logic, and dry-run execution mode.
"""

import sys
import os
import argparse
import logging
import requests

from ses_alert import send_ses_alert, send_alert, format_alert_email

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("monitor")


def parse_args(args=None):
    """
    Parses command line arguments and merges with environment variable defaults.

    Precedence: Command line flags > Environment variables > Defaults
    """
    default_url = os.getenv("TARGET_URL", "https://www.masterji.online")
    default_email = os.getenv("ALERT_EMAIL", "utkarshethics@gmail.com")
    env_dry_run = (
        os.getenv("DRY_RUN", "").lower() in ("true", "1", "yes")
        or os.getenv("MOCK_SES", "").lower() in ("true", "1", "yes")
    )

    parser = argparse.ArgumentParser(description="Uptime monitoring service with AWS SES alerting.")
    parser.add_argument("--url", type=str, default=default_url, help="Target URL to monitor")
    parser.add_argument("--email", type=str, default=default_email, help="Alert recipient email address")
    parser.add_argument("--dry-run", action="store_true", default=env_dry_run, help="Run in dry-run mode without live SES calls")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP request timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="Max retry attempts for failed checks")

    return parser.parse_args(args)


def check_uptime(url, timeout=5.0, retries=3):
    """
    Performs HTTP GET check on target URL with timeout and retry logic.

    Args:
        url (str): Target URL to perform HTTP check.
        timeout (float or tuple): Request timeout in seconds.
        retries (int): Maximum retry attempts.

    Returns:
        tuple: (is_up: bool, status_code: int or None, details: str)
    """
    last_status_code = None
    last_details = ""

    if isinstance(timeout, (int, float)):
        req_timeout = (min(3.05, float(timeout)), float(timeout))
    else:
        req_timeout = timeout

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Checking URL '{url}' (attempt {attempt}/{retries})...")
            response = requests.get(url, timeout=req_timeout, allow_redirects=True)
            response.raise_for_status()
            logger.info(f"Check succeeded for '{url}': HTTP {response.status_code}")
            return True, response.status_code, f"OK - HTTP status {response.status_code}"
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code if e.response is not None else None
            last_status_code = code
            last_details = f"HTTP Error {code}: {e}"
            logger.warning(f"Attempt {attempt}/{retries} failed for '{url}': {last_details}")
        except requests.exceptions.Timeout as e:
            last_status_code = None
            last_details = f"Connection timeout: {e}"
            logger.warning(f"Attempt {attempt}/{retries} timed out for '{url}': {last_details}")
        except requests.exceptions.RequestException as e:
            last_status_code = None
            last_details = f"Connection error: {e}"
            logger.warning(f"Attempt {attempt}/{retries} connection failed for '{url}': {last_details}")

    return False, last_status_code, last_details


def main():
    """Main process entrypoint."""
    try:
        args = parse_args()
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        logger.error(f"Configuration or CLI argument error: {e}")
        sys.exit(2)

    is_up, status_code, details = check_uptime(args.url, timeout=args.timeout, retries=args.retries)

    if is_up:
        logger.info(f"SUCCESS: Site '{args.url}' is UP (HTTP {status_code}).")
        sys.exit(0)
    else:
        logger.error(f"FAILURE: Site '{args.url}' is DOWN (HTTP {status_code}). Details: {details}")
        subject, body = format_alert_email(args.url, status_code, details)
        send_ses_alert(
            recipient=args.email,
            subject=subject,
            body=body,
            dry_run=args.dry_run,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
