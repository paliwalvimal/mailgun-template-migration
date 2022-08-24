import http
import os
from argparse import ArgumentParser, Namespace
from datetime import datetime
from itertools import product
from typing import List

import requests
from loguru import logger

from models.Flags import Action, Env
from models.TemplateModel import FullTemplate, BaseTemplate

MG_BASE_URL = os.environ.get('MG_BASE_URL', 'https://api.mailgun.net/v3')
MG_TEMPLATES_DOMAIN = os.environ.get('MG_TEMPLATES_DOMAIN')
MG_LOCAL_MAIL_DOMAIN = os.environ.get('MG_LOCAL_MAIL_DOMAIN')
MG_DEV_MAIL_DOMAIN = os.environ.get('MG_DEV_MAIL_DOMAIN')
MG_PROD_MAIL_DOMAIN = os.environ.get('MG_PROD_MAIL_DOMAIN')
MG_API_KEY = os.environ.get('MG_API_KEY')
TEMPLATES_URL = f"{MG_BASE_URL}/{MG_TEMPLATES_DOMAIN}/templates"


def read_arguments() -> Namespace:
    parser = ArgumentParser(description='MailGun template migrator')
    parser.add_argument('action', nargs='?', type=Action, default=Action.COPY,
                        help='choose which action would you like to do. only *copy* supported')
    parser.add_argument('env', type=Env, default=Env.DEV,
                        help='choose which environment to copy templates from. local, dev, prod or ALL')
    return parser.parse_args()


def mail_domain_resolver(env: Env) -> str:
    return {Env.LOCAL: MG_LOCAL_MAIL_DOMAIN,
            Env.DEV: MG_DEV_MAIL_DOMAIN,
            Env.PROD: MG_PROD_MAIL_DOMAIN}.get(env)


def delete_template_in_domain(template: FullTemplate, env_to_copy: Env):
    response = requests.delete(f'{MG_BASE_URL}/{mail_domain_resolver(env_to_copy)}/templates/{template.name}',
                               auth=('api', MG_API_KEY))
    if response.status_code != http.HTTPStatus.OK:
        logger.error(f" template {template.name} cannot be deleted from {env_to_copy.name} environment")
    else:
        logger.info(f" template {template.name} deleted successfully in {env_to_copy.name} environment")


def create_template_in_domain(template: FullTemplate, env_to_copy: Env):
    response = requests.post(f'{MG_BASE_URL}/{mail_domain_resolver(env_to_copy)}/templates', auth=('api', MG_API_KEY),
                             data={'name': template.name, 'description': template.description,
                                   'template': template.version.template,
                                   'tag': datetime.now().strftime('%Y-%m-%d_%H-%M')})
    if response.status_code != http.HTTPStatus.OK:
        logger.error(f" template {template.name} cannot be stored in {env_to_copy.name} environment")
        delete_template_in_domain(template, env_to_copy)
        create_template_in_domain(template, env_to_copy)
    else:
        logger.info(f" template {template.name} from={template.version.createdAt} stored successfully in {env_to_copy.name} environment")


def get_all_templates() -> List[FullTemplate]:
    templates: List[FullTemplate] = []
    logger.info(f"Fetching all templates under domain {MG_TEMPLATES_DOMAIN}")
    response = requests.get(TEMPLATES_URL, auth=('api', MG_API_KEY))
    if response.status_code != http.HTTPStatus.OK:
        logger.error(f"could not retrieve templates from {TEMPLATES_URL}")

    response = response.json()
    for template in response['items']:
        base_template = BaseTemplate(**template)
        full_response = requests.get(f"{MG_BASE_URL}/{MG_TEMPLATES_DOMAIN}/templates/{base_template.name}",
                                     auth=('api', MG_API_KEY),
                                     params={'active': 'yes'})
        if full_response.status_code != http.HTTPStatus.OK:
            logger.error(f" template {template.name} cannot be fully retrieved")
        else:
            templates.append(FullTemplate(**full_response.json()["template"]))

    return templates


def get_environments(env: Env) -> List[Env]:
    if env == Env.ALL:
        return [env.LOCAL, env.DEV, env.PROD]
    return [env]


def migrate_template(action: Action, env: Env):
    templates = get_all_templates()

    for template, env_to_copy in product(templates, get_environments(env)):
        if action == Action.COPY:
            create_template_in_domain(template, env_to_copy)


if __name__ == "__main__":
    arguments = read_arguments()
    migrate_template(arguments.action, arguments.env)
