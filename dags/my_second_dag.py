from datetime import datetime
import logging

from airflow import DAG
from airflow.operators.python_operator import PythonOperator

import pandas
import toolz

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'andresionek91',
    'start_date': datetime(2020, 5, 25),
    'depends_on_past': False,
    'provide_context': True
}

dag = DAG('my_second_dag',
          description='My second Airflow DAG',
          schedule_interval=None,
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

t1 >> t2
