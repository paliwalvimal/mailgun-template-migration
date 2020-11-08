## mailgun-template-migration

Migrate mailgun email templates from one domain to another

## Licence:
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

MIT Licence. See [Licence](LICENCE) for full details.

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