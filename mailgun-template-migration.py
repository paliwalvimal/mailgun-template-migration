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


def read_arguments() -> Namespace:
    parser = ArgumentParser(description='MailGun template migrator')
    parser.add_argument('action', nargs='?', type=Action, default=Action.COPY,
                        help='choose which action would you like to do. only *copy* supported')
    parser.add_argument('env', type=Env, default=Env.DEV,
                        help='choose which environment to copy templates from. local, dev, prod or ALL')
    return parser.parse_args()


def get_template(templates: List[BaseTemplate]) -> List[FullTemplate]:
    full_templates: List[FullTemplate] = []
    for template in templates:
        response = requests.get(f"{MG_BASE_URL}/{MG_TEMPLATES_DOMAIN}/templates/{template.name}",
                                auth=('api', MG_API_KEY),
                                params={'active': 'yes'})
        if response.status_code != http.HTTPStatus.OK:
            logger.error(f" template {template.name} cannot be fully retrieved")
        else:
            full_templates.append(FullTemplate(**response.json()["template"]))

    return full_templates


def mail_domain_resolver(env: Env) -> str:
    return {Env.LOCAL: MG_LOCAL_MAIL_DOMAIN,
            Env.DEV: MG_DEV_MAIL_DOMAIN,
            Env.PROD: MG_PROD_MAIL_DOMAIN}.get(env)


def create_template(template: FullTemplate, env_to_copy: Env):
    response = requests.post(f'{MG_BASE_URL}/{mail_domain_resolver(env_to_copy)}/templates', auth=('api', MG_API_KEY),
                             data={'name': template.name, 'description': template.description,
                                   'template': template.version.template,
                                   'tag': datetime.now().strftime('%Y-%m-%d_%H-%M')})
    if response.status_code != http.HTTPStatus.OK:
        logger.error(f" template {template.name} cannot be stored in {env_to_copy.name} environment")
    else:
        logger.info(f" template {template.name} stored successfully in {env_to_copy.name} environment")


def get_all_templates() -> List[BaseTemplate]:
    templates: List[BaseTemplate] = []
    logger.info(f"Fetching all templates under domain {MG_TEMPLATES_DOMAIN}")
    templates_url = f"{MG_BASE_URL}/{MG_TEMPLATES_DOMAIN}/templates"
    response = requests.get(templates_url, auth=('api', MG_API_KEY))
    if response.status_code != http.HTTPStatus.OK:
        logger.error(f"could not retrieve templates from {templates_url}")

    response = response.json()
    for template in response['items']:
        templates.append(BaseTemplate(**template))

    return templates


def get_environments(env: Env) -> List[Env]:
    if env == Env.ALL:
        return [env.LOCAL, env.DEV, env.PROD]
    return [env]


def migrate_template(action: Action, env: Env):
    templates = get_all_templates()

    full_templates = get_template(templates)

    for template, env_to_copy in product(full_templates, get_environments(env)):
        if action == Action.COPY:
            create_template(template, env_to_copy)


if __name__ == "__main__":
    arguments = read_arguments()
    migrate_template(arguments.action, arguments.env)
