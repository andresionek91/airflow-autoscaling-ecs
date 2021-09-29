from flask import Blueprint
from airflow.plugins_manager import AirflowPlugin
from backfill_plugin.backfill import Backfill

backfill_admin_view = Backfill(category="Admin", name="Backfill")
backfill_blueprint = Blueprint(
    "backfill_blueprint", __name__,
    template_folder='templates')


class AirflowBackfillPlugin(AirflowPlugin):
    name = "backfill_plugin"
    admin_views = [backfill_admin_view]
    flask_blueprints = [backfill_blueprint]
