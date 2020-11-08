## mailgun-template-migration

Migrate mailgun email templates from one domain to another

### Usage:
 - Set required environment variables
 - Execute python script

### Environment Variables:
```bash
MG_OLD_MAIL_DOMAIN=''  # Domain name under which template exists
MG_NEW_MAIL_DOMAIN=''  # Domain name to which template needs to be copied or moved to
MG_API_KEY=''          # Mailgun API Key
```

### Command:
```bash
python3 mailgun-template-migration.py {copy|move}
```