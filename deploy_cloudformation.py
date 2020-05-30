import boto3
import os
import re
import logging
from zipfile import ZipFile
from botocore.exceptions import ClientError
from tempfile import NamedTemporaryFile

STACK_TAGS = [
    {
        'Key': 'Service',
        'Value': 'airflow'
    },
    {
        'Key': 'Owner',
        'Value': 'data-engineering'
    },
]


class StackFailed(Exception):
    pass


logging.basicConfig(level=logging.INFO)
cloudformation_client = boto3.client('cloudformation')
cloudformation_resource = boto3.resource('cloudformation')

s3_client = boto3.client('s3')


def _get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def get_cloudformation_templates():
    cf_templates = []
    files = os.listdir(_get_abs_path("cloudformation"))
    files.sort()
    for filename in files:
        path = _get_abs_path("cloudformation") + "/" + filename
        with open(path) as f:
            template_body = f.read()

        cf_template = {
            'stack_name': 'cfn-' + re.search('(?<=_)(.*)(?=.yml)', filename).group(1),
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
        StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE']
    )

    return [stack['StackName'] for stack in response['StackSummaries']]


def update_stack(stack_name, template_body, **kwargs):
    try:
        cloudformation_client.update_stack(
            StackName=stack_name,
            Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
            TemplateBody=template_body,
            Tags=STACK_TAGS
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
        Tags=STACK_TAGS
    )

    cloudformation_client.get_waiter('stack_create_complete').wait(
        StackName=stack_name,
        WaiterConfig={'Delay': 5, 'MaxAttempts': 600}
    )

    cloudformation_client.get_waiter('stack_exists').wait(StackName=stack_name)
    logging.info(f'CREATE COMPLETE')


def create_or_update_stacks():
    cf_templates = get_cloudformation_templates()
    existing_stacks = get_existing_stacks()

    for cf_template in cf_templates:
        if cf_template['stack_name'] in existing_stacks:
            logging.info('UPDATING STACK {stack_name}'.format(**cf_template))
            update_stack(**cf_template)
        else:
            logging.info('CREATING STACK {stack_name}'.format(**cf_template))
            create_stack(**cf_template)

        copy_rotate_lambda_functions_to_s3(cf_template['stack_name'])


def copy_rotate_lambda_functions_to_s3(stack_name):
    stack = cloudformation_resource.Stack(stack_name)
    bucket_output = [output for output in stack.outputs if output['ExportName'] == 'storage-RotationLambdaCodeBucketName']

    if not bucket_output:
        return

    bucket_name = bucket_output[0]['OutputValue']

    lambdas = os.listdir(_get_abs_path("lambda"))
    for lambdaf in lambdas:
        path = _get_abs_path("lambda") + "/" + lambdaf
        filename = re.search('(.*)(?=.py)', lambdaf).group(1)
        logging.info(f'Copying lambda function {filename} to s3 {bucket_name}')

        with open(path) as f:
            buffer = f.read()

        temp_file = NamedTemporaryFile()
        with ZipFile(temp_file.name, 'w') as zip:
            zip.writestr(lambdaf, buffer)

        s3_client.put_object(
            Bucket=bucket_name,
            Key=f'{filename}/lambda_function.zip',
            Body=temp_file
        )


def execute():
    validate_templates()
    create_or_update_stacks()


if __name__ == '__main__':
    execute()
