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

with DAG('dbt',
         description='DAG to run dbt',
         schedule_interval='0 1 * * *',
         catchup=False,
         default_args=default_args) as dag:

    t1 = ECSOperator(
        task_id="dbt_run",
        dag=dag,
        aws_conn_id="aws_default",
        cluster="airflow-production-ecs-cluster",
        task_definition="production-dbt-image",
        launch_type="FARGATE",
        overrides={
            "containerOverrides": [
                {
                    "name": "production-dbt-image",
                    "command": ["dbt", "run"],
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