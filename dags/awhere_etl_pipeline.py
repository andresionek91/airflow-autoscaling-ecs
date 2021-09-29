from airflow import DAG
from airflow.operators.awhere_plugin import AwhereToS3Operator
from airflow.operators.s3_file_transform_operator import S3FileTransformOperator
from datetime import date, timedelta, datetime
import os

start_day = datetime.now() - timedelta(days=1)
yesterday = date.today() - timedelta(days=1)
AIRFLOW_HOME = os.environ['AIRFLOW_HOME']

default_args = {
    'owner': 'airflow',
    'depends_on': False,
    'start_date': start_day,
    'email': ['tkayneftw.aws@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'schedule_interval': '@daily'
}

with DAG(
    dag_id='awhere_etl_pipeline',
    default_args=default_args,
    description='Ingest and process climate data of Denver daily',
    catchup=False
) as dag:

    #ingest data
    ingestion_task = AwhereToS3Operator(
        task_id='denver_climate_ingestion',
        dataset_url='https://api.awhere.com/v2/weather/fields/{}/observations/{}'.format('denver',"{{ execution_date.strftime('%Y-%m-%d') }}"),
        s3_bucket='awhere-etl',
        s3_key='s3://awhere-etl/ingest/{}/climate_{}.json'.format('denver',"{{ execution_date.strftime('%Y-%m-%d') }}"),
        replace=True,
    )

    #transform data
    transformation_task = S3FileTransformOperator(
        task_id='denver_climate_transformation',
        source_s3_key='s3://awhere-etl/ingest/{}/climate_{}.json'.format('denver',"{{ execution_date.strftime('%Y-%m-%d') }}"),
        dest_s3_key='s3://awhere-etl/transformed/{}/climate_{}.json'.format('denver',"{{ execution_date.strftime('%Y-%m-%d') }}"),
        replace=True,
        transform_script=AIRFLOW_HOME + '/scripts/etl/awhere.py'
    )

    ingestion_task >> transformation_task


