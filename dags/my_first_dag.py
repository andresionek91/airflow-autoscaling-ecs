from datetime import datetime
import logging

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

import pandas
import toolz

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'andresionek91',
    'start_date': datetime(2020, 5, 20),
    'depends_on_past': False,
    'provide_context': True
}

dag = DAG('my_first_dag',
          description='My first Airflow DAG',
          schedule_interval='*/5 * * * *',
          catchup=False,
          default_args=default_args)


def task_1(**kwargs):
    output = {'output': 'hello world 1', 'execution_time': str(datetime.now())}
    logger.info(output)
    logger.info(f'Pandas version: {pandas.__version__}')
    logger.info(f'Toolz version: {toolz.__version__}')
    return output


def task_2(**kwargs):
    ti = kwargs['ti']
    output_task_1 = ti.xcom_pull(key='return_value', task_ids='task_1')
    logger.info(output_task_1)
    return {'output': 'hello world 2', 'execution_time': str(datetime.now())}


def task_3(**kwargs):
    logger.info('Log from task 3')
    return {'output': 'hello world 3', 'execution_time': str(datetime.now())}


t1 = PythonOperator(
    task_id='task_1',
    dag=dag,
    python_callable=task_1
)

t2 = PythonOperator(
    task_id='task_2',
    dag=dag,
    python_callable=task_2
)

t3 = PythonOperator(
    task_id='task_3',
    dag=dag,
    python_callable=task_3
)

t1 >> [t2, t3]
