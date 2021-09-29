from tempfile import NamedTemporaryFile
from airflow.operators import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.hooks.S3_hook import S3Hook
import logging as log
import requests
import json
import os
from datetime import date

TOKEN_URL = os.environ['AWHERE_TOKEN_URL']
ENCODED_KEY = os.environ['AWHERE_ENCODED_KEY']

class AwhereToS3Operator(BaseOperator):
    """
    Send raw JSON data to s3 from Awhere API

    :param dataset_url:         The endpoint of the dataset json
    :type dataset_url:          string
    :param s3_conn_id:          The destination s3 connection id.
    :type s3_conn_id:           string
    :param s3_bucket:           The destination s3 bucket.
    :type s3_bucket:            string
    :param s3_key:              The destination s3 key.
    :type s3_key:               string
    """

    template_fields = ("dataset_url","s3_key")

    @apply_defaults
    def __init__(self, dataset_url, s3_bucket, s3_key, s3_conn_id='aws_default', *args, **kwargs):
        super(AwhereToS3Operator, self).__init__(*args, **kwargs)
        self.dataset_url = dataset_url
        self.s3_conn_id = s3_conn_id
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key

    @staticmethod
    def _get_token():
        headers = {
            'Authorization': 'Basic ' + ENCODED_KEY,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body = {
            'grant_type':'client_credentials'
        }
        res = requests.post(TOKEN_URL,headers=headers,data=body)
        token = json.loads(res.text)
        return str(token['access_token'])

    def execute(self, context):
        # validate and raise error if missing dataset url or s3_key
        log.info('Retrieving api token...')
        access_token = self._get_token()
        with NamedTemporaryFile("w") as tmp:

            log.info('Fetching data from api endpoint {}'.format(self.dataset_url))
            res = requests.get(self.dataset_url, headers={'Authorization':'Bearer ' + access_token})
            # data = json.dumps(res.text)
            data = res.json()

            log.info("Writing json results to: {0}".format(tmp.name))
            tmp.write(json.dumps(data))
            tmp.flush()

            log.info('Saving json data to s3 destination: {}'.format(self.s3_key))
            dest_s3 = S3Hook(aws_conn_id=self.s3_conn_id)
            dest_s3.load_string(
                string_data=json.dumps(data),
                key=self.s3_key
            )
            # dest_s3.load_file(
            #             filename=tmp.name,
            #             key=self.s3_key,
            #             bucket_name=self.s3_bucket,
            #             replace=True
            #         )

            tmp.close()

        log.info('Successfully uploaded file to S3 bucket')

