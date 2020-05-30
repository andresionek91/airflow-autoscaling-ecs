import logging

from airflow.models import BaseOperator
from airflow.plugins_manager import AirflowPlugin
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger('airflow.my_first_operator')

class MyFirstOperator(BaseOperator):

    @apply_defaults
    def __init__(self, my_operator_param, *args, **kwargs):
        self.operator_param = my_operator_param
        super(MyFirstOperator, self).__init__(*args, **kwargs)

    def execute(self, context):
        logger.info('Hello World!')
        logger.info('operator_param: %s', self.operator_param)

class MyFirstPlugin(AirflowPlugin):
    name = 'my_first_plugin'
    operators = [MyFirstOperator]
