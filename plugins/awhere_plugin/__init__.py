from airflow.plugins_manager import AirflowPlugin
from awhere_plugin.operators.awhere_to_s3_operator import AwhereToS3Operator

class AwherePlugin(AirflowPlugin):
	name = "awhere_plugin"
	operators = [AwhereToS3Operator]
	hooks = []
	executors = []
	macros = []
	admin_views = []
	flask_blueprints = []
	menu_links = []


