from datetime import datetime
import logging

from airflow import DAG
from airflow.contrib.operators.aws_athena_operator import AWSAthenaOperator

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'andresionek91',
    'start_date': datetime(2020, 5, 20),
    'depends_on_past': False,
    'provide_context': True
}


with DAG('sessions',
         description='DAG pra sessionizar usuarios',
         schedule_interval='*/15 * * * *',
         catchup=False,
         default_args=default_args) as dag:

    t1 = AWSAthenaOperator(
        task_id='query_sessoes',
        dag=dag,
        query="""
        with step_1 as (
        select 
        user_domain_id,
        date_parse(event_timestamp,'%Y-%m-%d %H:%i:%s.%f') as timestamp,
        LAG(date_parse(event_timestamp,'%Y-%m-%d %H:%i:%s.%f'), 1) OVER (PARTITION BY user_domain_id ORDER BY event_timestamp) as  previous_timestamp
        from data_lake_raw.atomic_events
        ), step_2 as (
        select 
        user_domain_id,
        timestamp,
        previous_timestamp,
        CASE WHEN date_diff('minute', previous_timestamp, timestamp) >= 30 THEN 1 ELSE 0 END as new_session
        from step_1
        ),
        step_3 as (
        select 
        user_domain_id,
        timestamp,
        previous_timestamp,
        new_session,
        SUM(new_session) OVER (PARTITION BY user_domain_id ORDER BY timestamp ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS session_idx
        from step_2
        )
        select 
        user_domain_id || cast(session_idx as varchar) as  session_id,
        * 
        from step_3
        """,
        database="data_lake_raw",
        output_location="s3://s3-belisco-production-data-lake-curated/sessions_airflow/",
        aws_conn_id='aws_default'
    )

    t1
