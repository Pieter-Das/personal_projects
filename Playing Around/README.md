# Outlook mailbox reader

Python helper that authenticates to Microsoft 365 via Microsoft Graph (device-code flow) and prints a summary of the most recent emails in any folder.

## Prerequisites

1. Microsoft 365 / Outlook account that you can log into via https://outlook.office.com.
2. Azure AD app registration with **delegated** permission `Mail.Read` (and admin consent if your tenant requires it).
   - Redirect URI can be set to `https://login.microsoftonline.com/common/oauth2/nativeclient` for testing.
   - Note the **Application (client) ID** and **Directory (tenant) ID** from the registration overview.
3. Python 3.9+ installed locally.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file (never commit real secrets) with:

```
MS_CLIENT_ID=aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee
MS_TENANT_ID=your-tenant-guid-or-common
```

If you want to target the "common" endpoint because the account lives in a personal tenant, set `MS_TENANT_ID=common`.

## Usage

```bash
python outlook_reader.py --top 10 --folder Inbox --preview
```

The first run prompts you to authenticate using the Microsoft device-code flow. Follow the printed instructions, sign in, and approve the requested permissions. Subsequent runs reuse the cached token until it expires/revocation occurs.

### Flags

- `--folder` defaults to `Inbox`. Use subfolder names such as `"Archive"` or `"SentItems"`.
- `--top` controls how many messages to retrieve (max 1000 per Graph API docs; practical limits are smaller).
- `--preview` includes the text preview snippet. Skip it to reduce payload.

## Next steps

- Adjust `SCOPES` (in `outlook_reader.py`) if you later need write access (`Mail.ReadWrite`) or other Graph capabilities.
- Extend `fetch_messages` to filter, search, or download attachments once you know the specific data you need.
