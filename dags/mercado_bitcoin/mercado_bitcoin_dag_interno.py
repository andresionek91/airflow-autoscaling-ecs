from datetime import datetime
import logging

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.S3_hook import S3Hook
import requests
import yaml
import sys
from airflow.models import Variable
from backoff import on_exception, constant
from ratelimit import limits, RateLimitException
import boto3
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)
config = Variable.get("cryptocurrency", deserialize_json=True)

default_args = {
    'owner': 'andresionek91',
    'start_date': datetime(2021, 1, 1),
    'depends_on_past': False,
    'provide_context': True
}

dag = DAG('mercado_bitcoin_dag_interno',
          description='Extrai dados do sumario diario do mercado bitcoin.',
          schedule_interval='0 0 * * *',
          catchup=True,
          default_args=default_args)


@on_exception(constant, RateLimitException, interval=60, max_tries=3)
@limits(calls=20, period=60)
@on_exception(constant,
              requests.exceptions.HTTPError,
              max_tries=3,
              interval=10)
def get_daily_summary(coin, year, month, day):
    endpoint = f'https://www.mercadobitcoin.net/api/{coin}/day-summary/{year}/{month}/{day}'

    logger.info(f'Getting data from API with: {endpoint}')

    response = requests.get(endpoint)
    response.raise_for_status()

    return response.json()


logging.getLogger().setLevel(logging.INFO)

client = boto3.client('s3')


def extract_and_upload(date, **kwargs):
    year, month, day = date.split('-')
    for coin in config['coins']:
        json_data = get_daily_summary(coin, int(year), int(month), int(day))
        string_data = json.dumps(json_data)
        now = datetime.now()
        now_string = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
        S3Hook(
            aws_conn_id='aws_default'
        ).load_string(
            string_data=string_data,
            key=f"cryptocurrency_interno/{coin}/execution_date={date}/cryptocurrency_interno_{coin}_{now_string}.json",
            bucket_name=config['bucket'],
        )


task_1 = PythonOperator(
    task_id='extract_and_upload',
    dag=dag,
    python_callable=extract_and_upload,
    op_kwargs={'date': '{{ ds }}'},
)


task_1
