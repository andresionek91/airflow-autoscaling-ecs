import docker
import logging
import os
import base64
from utils import _get_abs_path
from utils import generate_hash
import boto3

logging.basicConfig(level=logging.INFO)

docker_client = docker.from_env()

ENVIRONMENT = os.environ['ENVIRONMENT']
AWS_REGION = os.environ['AWS_REGION']
ECR_REPO_NAME = f'airflow-{ENVIRONMENT}'
IMAGE_TAG = 'latest'


class DockerException(Exception): pass


def connect_to_ecr():
    client = boto3.client('ecr')
    token = client.get_authorization_token()

    logging.info(f'CONNECTED TO ECR')

    b64token = token['authorizationData'][0]['authorizationToken'].encode('utf-8')
    username, password = base64.b64decode(b64token).decode('utf-8').split(':')
    registry = token['authorizationData'][0]['proxyEndpoint']
    docker_client.login(username=username, password=password, registry=registry)

    return registry


def build_image():
    logging.info(f'BUILDING IMAGE: {ECR_REPO_NAME}:{IMAGE_TAG}')
    image, buildlog = docker_client.images.build(path=_get_abs_path(''), rm=True, tag=f'{ECR_REPO_NAME}:{IMAGE_TAG}')

    for log in buildlog:
        if log.get('stream'):
            logging.info(log.get('stream'))

    return image


def tag_and_push_to_ecr(image, tag):
    registry = connect_to_ecr()
    logging.info(f'Pushing image to ECR: {ECR_REPO_NAME}:{tag}')
    ecr_repo_name = '{}/{}'.format(registry.replace('https://', ''), ECR_REPO_NAME)
    image.tag(ecr_repo_name, tag)
    push_log = docker_client.images.push(ecr_repo_name, tag=tag)

    if 'errorDetail' in push_log:
        logging.error(push_log)
        raise DockerException()
    logging.info(push_log)


def update_airflow_image():
    image = build_image()
    tag_and_push_to_ecr(image, IMAGE_TAG)
    hash_tag = generate_hash(16)
    tag_and_push_to_ecr(image, hash_tag)
