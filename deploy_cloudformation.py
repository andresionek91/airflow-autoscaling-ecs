import boto3
import os
import re
import json
import logging
from botocore.exceptions import ClientError
import click

from utils import _get_abs_path
from utils import render_template
from utils import create_default_tags
from utils import create_fernet_key
from utils import get_aws_account_id


logging.basicConfig(level=logging.INFO)
cloudformation_client = boto3.client('cloudformation')
cloudformation_resource = boto3.resource('cloudformation')
s3_client = boto3.client('s3')
ecs_client = boto3.client('ecs')


def get_cloudformation_templates(reverse=False):
    cf_templates = []
    files = os.listdir(_get_abs_path("cloudformation"))
    files.sort(reverse=reverse)
    create_fernet_key()

    for filename in files:
        path = _get_abs_path("cloudformation") + "/" + filename
        with open(path) as f:
            template_body = f.read()
        logging.info(f'Rendering template {filename}')
        template_body = render_template(template_body)
        cf_template = {
            'stack_name': 'cfn-' + re.search('(?<=_)(.*)(?=.yml.j2)', filename).group(1),
            'template_body': template_body,
            'filename': filename
         }
        cf_templates.append(cf_template)

    return cf_templates


def validate_templates():
    cf_templates = get_cloudformation_templates()
    for cf_template in cf_templates:
        logging.info('Validating CF template {}'.format(cf_template['filename']))
        cloudformation_client.validate_template(
            TemplateBody=cf_template['template_body']
        )


def get_existing_stacks():
    response = cloudformation_client.list_stacks(
        StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE', 'UPDATE_ROLLBACK_COMPLETE']
    )

    return [stack['StackName'] for stack in response['StackSummaries']]


def update_stack(stack_name, template_body, **kwargs):
    try:
        cloudformation_client.update_stack(
            StackName=stack_name,
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
            TemplateBody=template_body,
            Tags=create_default_tags()
        )

    except ClientError as e:
        if 'No updates are to be performed' in str(e):
            logging.info(f'SKIPPING UPDATE: No updates to be performed at stack {stack_name}')
            return e

    cloudformation_client.get_waiter('stack_update_complete').wait(
        StackName=stack_name,
        WaiterConfig={'Delay': 5, 'MaxAttempts': 600}
    )

    cloudformation_client.get_waiter('stack_exists').wait(StackName=stack_name)
    logging.info(f'UPDATE COMPLETE')


def create_stack(stack_name, template_body, **kwargs):
    cloudformation_client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
        TimeoutInMinutes=30,
        OnFailure='ROLLBACK',
        Tags=create_default_tags()
    )

    cloudformation_client.get_waiter('stack_create_complete').wait(
        StackName=stack_name,
        WaiterConfig={'Delay': 5, 'MaxAttempts': 600}
    )

    cloudformation_client.get_waiter('stack_exists').wait(StackName=stack_name)
    logging.info(f'CREATE COMPLETE')


def create_or_update_stacks(is_foundation):
    cf_templates = get_cloudformation_templates()
    cf_templates = filter_infra_templates(cf_templates, is_foundation)
    existing_stacks = get_existing_stacks()

    for cf_template in cf_templates:
        if cf_template['stack_name'] in existing_stacks:
            logging.info('UPDATING STACK {stack_name}'.format(**cf_template))
            update_stack(**cf_template)
        else:
            logging.info('CREATING STACK {stack_name}'.format(**cf_template))
            create_stack(**cf_template)


def destroy_stacks():
    if not click.confirm('You are about to delete all your Airflow Infrastructure. Do you want to continue?', default=False):
        return
    cf_templates = get_cloudformation_templates(reverse=True)
    existing_stacks = get_existing_stacks()

    for cf_template in cf_templates:
        if cf_template['stack_name'] in existing_stacks:
            logging.info('DELETING STACK {stack_name}'.format(**cf_template))
            delete_stack(**cf_template)


def delete_stack(stack_name, **kwargs):
    cloudformation_client.delete_stack(
        StackName=stack_name
    )

    cloudformation_client.get_waiter('stack_delete_complete').wait(
        StackName=stack_name,
        WaiterConfig={'Delay': 5, 'MaxAttempts': 600}
    )

    logging.info(f'DELETE COMPLETE')


def filter_infra_templates(cf_templates, is_foundation):
    if is_foundation:
        return [x for x in cf_templates if 'airflow' not in x['stack_name']]
    else:
        return [x for x in cf_templates if 'airflow' in x['stack_name']]


def update_ecs_service(airflow_service):
    aws_account_id = get_aws_account_id()
    ecs_service = render_template('{{ serviceName }}-{{ ENVIRONMENT }}-{airflow_service}').format(airflow_service=airflow_service)
    ecs_cluster = render_template('arn:aws:ecs:{{ AWS_REGION }}:{aws_account_id}:cluster/{{ serviceName }}-{{ ENVIRONMENT }}-ecs-cluster').format(aws_account_id=aws_account_id)
    logging.info(f'RESTARTING SERVICE: {ecs_service}')
    ecs_client.update_service(cluster=ecs_cluster, service=ecs_service, forceNewDeployment=True)


def restart_airflow_ecs():
    update_ecs_service('workers')
    update_ecs_service('flower')
    update_ecs_service('scheduler')
    update_ecs_service('webserver')


def log_outputs():
    cf_templates = get_cloudformation_templates(reverse=True)
    outputs = {}
    logging.info(f'\n\n\n## OUTPUTS ##')
    for cf_template in cf_templates:
        stack_name = cf_template['stack_name']
        stack = cloudformation_resource.Stack(stack_name)
        outputs = {
            stack_name: stack.outputs,
            **outputs
        }
    logging.info(json.dumps(outputs, indent=4))

    return outputs
