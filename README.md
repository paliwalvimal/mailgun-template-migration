## mailgun-template-migration

![License](https://img.shields.io/github/license/paliwalvimal/mailgun-template-migration?style=for-the-badge) ![CodeQL](https://img.shields.io/github/workflow/status/paliwalvimal/mailgun-template-migration/codeql/main?label=CodeQL&style=for-the-badge) ![Commit](https://img.shields.io/github/last-commit/paliwalvimal/mailgun-template-migration?style=for-the-badge) ![Release](https://img.shields.io/github/v/release/paliwalvimal/mailgun-template-migration?style=for-the-badge)

Migrate mailgun email templates from one domain to another

### Usage:
 - Set required environment variables
 - Execute python script

### Environment Variables:
```bash
MG_BASE_URL='https://api.mailgun.net/v3'    # Mailgun API base URL
MG_OLD_MAIL_DOMAIN='abc.com'                # Domain name under which template exists
MG_NEW_MAIL_DOMAIN='xyz.com'                # Domain name to which template needs to be copied or moved to
MG_API_KEY='xxxxxxxxxx'                     # Mailgun API Key
```

### Command:
```bash
python3 mailgun-template-migration.py {copy|move}
```