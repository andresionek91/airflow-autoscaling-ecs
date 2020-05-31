import os
from jinja2 import Template
from yaml import safe_load
import boto3
from cryptography.fernet import Fernet
import logging
import json


logging.basicConfig(level=logging.INFO)


def _get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def render_template(template):
    with open(_get_abs_path("service.yml")) as f:
        service_config = safe_load(f)

    return Template(template).render({**service_config, **dict(os.environ)})


def create_fernet_key():
    """
    Try to find fernet key in AWS Secrets Manager.
    If resource does not exist, create a new key.
    Set key as environment variable to be used by CF template.
    """

    client = boto3.client('secretsmanager')

    try:
        response = client.get_secret_value(
            SecretId=render_template('{{ serviceName }}-{{ ENVIRONMENT }}-fernet-key'),
        )
        os.environ['FERNET_KEY'] = json.loads(response['SecretString'])['fernet_key']
        logging.info('FERNET KEY found in Secrets Manager.')
    except client.exceptions.ResourceNotFoundException:
        fernet_key = Fernet.generate_key().decode()
        os.environ['FERNET_KEY'] = fernet_key
        logging.info('FERNET KEY not found in Secrets Manager. New key created. It will be uploaded to Secrets Manager.')


def create_default_tags():
    tags_template = '''[
        {"Key": "Owner","Value": "{{ owner }}"},
        {"Key": "Service", "Value": "{{ serviceName }}"},
        {"Key": "Environment", "Value": "{{ ENVIRONMENT }}"}
        ]'''
    tags = json.loads(render_template(tags_template))
    return tags
