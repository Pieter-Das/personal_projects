"""
Utility script to authenticate against Microsoft 365 via Microsoft Graph and read Outlook messages.

The script uses the device-code OAuth flow so you can grant access without embedding credentials.
Fill in the environment variables (see README.md) and run:

    python outlook_reader.py --top 5 --folder Inbox
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import requests
from dotenv import load_dotenv
from msal import PublicClientApplication

GRAPH_API_ROOT = "https://graph.microsoft.com/v1.0"
SCOPES = ["Mail.Read"]

# Load variables from a .env file if present.
load_dotenv(dotenv_path=Path(".env"))


class ConfigurationError(RuntimeError):
    """Raised when required configuration is missing."""


class AuthenticationError(RuntimeError):
    """Raised when acquiring an access token fails."""


@dataclass
class MessageSummary:
    subject: str
    sender: str
    received: str
    preview: Optional[str]


def load_required_env(var_name: str) -> str:
    """Fetch an environment variable or raise with a helpful message."""
    value = os.getenv(var_name)
    if not value:
        raise ConfigurationError(f"Missing required environment variable: {var_name}")
    return value


def acquire_token(client_id: str, tenant_id: str) -> str:
    """Authenticate via device code flow and return an access token."""
    authority = f"https://login.microsoftonline.com/{tenant_id}"
    app = PublicClientApplication(client_id=client_id, authority=authority)

    # Try cached account first to avoid repeated prompts.
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if "access_token" in result:
            return result["access_token"]

    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise AuthenticationError("Failed to initiate device flow. Check app registration permissions.")

    print(flow["message"])
    result = app.acquire_token_by_device_flow(flow)
    if "access_token" not in result:
        raise AuthenticationError(result.get("error_description", "Unknown authentication failure"))
    return result["access_token"]


def build_headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }


def fetch_messages(
    headers: Dict[str, str],
    folder: str,
    top: int,
    select_fields: Iterable[str],
    include_preview: bool,
) -> List[MessageSummary]:
    """
    Fetch messages from the specified folder, returning basic metadata.
    The API call uses $select to minimize payload size.
    """

    select_parts = list(select_fields)
    if include_preview:
        select_parts.append("bodyPreview")

    params = {
        "$top": str(top),
        "$orderby": "receivedDateTime DESC",
        "$select": ",".join(select_parts),
    }
    url = f"{GRAPH_API_ROOT}/me/mailFolders/{folder}/messages"
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    summaries: List[MessageSummary] = []
    for item in response.json().get("value", []):
        sender = item.get("from", {}).get("emailAddress", {})
        summaries.append(
            MessageSummary(
                subject=item.get("subject") or "(no subject)",
                sender=sender.get("name") or sender.get("address") or "(unknown sender)",
                received=item.get("receivedDateTime", ""),
                preview=item.get("bodyPreview"),
            )
        )
    return summaries


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read Outlook messages via Microsoft Graph.")
    parser.add_argument("--folder", default="Inbox", help="Mail folder name (default: Inbox)")
    parser.add_argument("--top", type=int, default=5, help="Number of messages to fetch (default: 5)")
    parser.add_argument("--preview", action="store_true", help="Include body preview text")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        client_id = load_required_env("MS_CLIENT_ID")
        tenant_id = load_required_env("MS_TENANT_ID")
    except ConfigurationError as exc:
        print(exc, file=sys.stderr)
        return 1

    try:
        token = acquire_token(client_id, tenant_id)
    except AuthenticationError as exc:
        print(f"Authentication failed: {exc}", file=sys.stderr)
        return 1

    headers = build_headers(token)

    select_fields = ("receivedDateTime", "subject", "from")
    try:
        messages = fetch_messages(headers, args.folder, args.top, select_fields, args.preview)
    except requests.HTTPError as exc:
        print(f"Graph API request failed: {exc} - {exc.response.text}", file=sys.stderr)
        return 1

    if not messages:
        print("No messages returned.")
        return 0

    for idx, message in enumerate(messages, start=1):
        print(f"{idx}. {message.subject}")
        print(f"   From: {message.sender}")
        print(f"   Received: {message.received}")
        if args.preview and message.preview:
            print(f"   Preview: {message.preview.strip()}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
