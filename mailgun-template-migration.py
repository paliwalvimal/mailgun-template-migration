import requests
import sys
import os

MG_BASE_URL = os.environ.get('MG_BASE_URL', 'https://api.mailgun.net/v3')
MG_OLD_MAIL_DOMAIN = os.environ.get('MG_OLD_MAIL_DOMAIN', None)
MG_NEW_MAIL_DOMAIN = os.environ.get('MG_NEW_MAIL_DOMAIN', None)
MG_API_KEY = os.environ.get('MG_API_KEY', None)

def get_template(name):
    r = requests.get('{}/{}/templates/{}'.format(MG_BASE_URL, MG_OLD_MAIL_DOMAIN, name), auth=('api', MG_API_KEY), params={'active': 'yes'})
    if r.status_code == 200:
        return r.json()['template']
    else:
        return False

def create_template(name, description, template):
    r = requests.post('{}/{}/templates'.format(MG_BASE_URL, MG_NEW_MAIL_DOMAIN), auth=('api', MG_API_KEY), data={'name': name, 'description': description, 'template': template})
    if r.status_code == 200 and r.json()['message'] == 'template has been stored':
        return r.json()['template']
    else:
        return False

def delete_template(name):
    r = requests.post('{}/{}/templates/{}'.format(MG_BASE_URL, MG_OLD_MAIL_DOMAIN, name), auth=('api', MG_API_KEY))
    if r.status_code == 200 and r.json()['message'] == 'template has been deleted':
        return True
    else:
        return False

def get_all_templates():
    templateNames = []
    params = {}
    print('Fetching all templates under domain {}'.format(MG_OLD_MAIL_DOMAIN))
    while True:
        r = requests.get('{}/{}/templates'.format(MG_BASE_URL, MG_OLD_MAIL_DOMAIN), auth=('api', MG_API_KEY), params=params)
        if r.status_code == 200:
            resp = r.json()
            for item in resp['items']:
                templateNames.append(item['name'])

            if len(resp['items']) > 0:
                params['page'] = 'next'
                params['p'] = resp['items'][len(resp['items']) - 1]['name']
            else:
                break
        else:
            break

    return templateNames

def migrate_template(operation):
    templateNames = get_all_templates()
    print('Template(s) to {}: {}'.format(operation, templateNames if len(templateNames) > 0 else 'None'))
    for templateName in templateNames:
        print('Copying template {} to domain {}'.format(templateName, MG_NEW_MAIL_DOMAIN))
        resp = get_template(templateName)
        r = create_template(templateName, resp['description'], resp['version']['template'])
        print('Template {} created in new domain'.format(templateName) if r else 'Failed to create template {} in new domain'.format(templateName))
        if operation == 'move':
            r = delete_template(templateName)
            print('Template {} deleted from old domain'.format(templateName) if r else 'Failed to delete template {} from old domain'.format(templateName))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Argument not found. Usage: python3 mailgun-template-migration.py [copy | move]')
        exit(1)
    elif MG_OLD_MAIL_DOMAIN is None or MG_NEW_MAIL_DOMAIN is None or MG_API_KEY is None:
        print('Environment variables MG_OLD_MAIL_DOMAIN, MG_NEW_MAIL_DOMAIN and MG_API_KEY are required. Current values:\nMG_OLD_MAIL_DOMAIN: {}\nMG_NEW_MAIL_DOMAIN: {}\nMG_API_KEY: {}'.format(MG_OLD_MAIL_DOMAIN, MG_NEW_MAIL_DOMAIN, MG_API_KEY))
        exit(1)
    elif sys.argv[1] != 'copy' and sys.argv[1] != 'move':
        print('Invalid argument. Usage: python3 mailgun-template-migration.py [copy | move]')
        exit(1)
    else:
        migrate_template(sys.argv[1])
