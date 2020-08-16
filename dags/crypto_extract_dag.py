from datetime import datetime
import logging

from airflow import DAG
from airflow.contrib.operators.ecs_operator import ECSOperator
from airflow.models import Variable

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'andresionek91',
    'start_date': datetime(2020, 5, 20),
    'depends_on_past': False,
    'provide_context': True
}

execution_date = '{{ ds }}'  # Access execution date

with DAG('crypto_extract',
         description='DAG to extract Daily Summaries from MercadoBitcoin',
         schedule_interval='* 1 * * *',
         catchup=True,
         default_args=default_args) as dag:

    t1 = ECSOperator(
        task_id="crypto_extract",
        dag=dag,
        aws_conn_id="aws_default",
        cluster="airflow-dev-ecs-cluster",
        task_definition="dev-crypto-extract-image",
        launch_type="FARGATE",
        overrides={
            "containerOverrides": [
                {
                    "name": "dev-crypto-extract-image",
                    "command": ["python", "main.py", execution_date],
                    "environment": [
                        {
                            'name': 'AWS_ACCESS_KEY_ID',
                            'value': 'string'
                        }
                    ]
                }
            ],
        },
        network_configuration = {
            "awsvpcConfiguration": {
                "securityGroups": [Variable.get("security-group")],
                "subnets": [Variable.get("subnet")],
                "assignPublicIp": "ENABLED"
            }
        }
    )

    t1