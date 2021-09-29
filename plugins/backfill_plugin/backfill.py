import subprocess
import json
import flask
from flask import request
from flask_admin import BaseView, expose


class Backfill(BaseView):

    @expose('/')
    def base(self):
        output = subprocess.check_output(
            'airflow list_dags', shell=True).split()
        dags = output[(output.index(b'DAGS') + 2):]
        return self.render("backfill_page.html",
                           dags=[dag.decode('utf8') for dag in dags])

    @expose('/backfill')
    def run_backfill(self):
        cmd = self._get_backfill_command(request.args.get("dag_name"),
                                         request.args.get("task_name"),
                                         request.args.get("start_date"),
                                         request.args.get("end_date"))

        subprocess.Popen(cmd, shell=True)
        response = json.dumps({'submitted': True})
        return flask.Response(response, mimetype='text/json')

    def _get_backfill_command(self, dag_name, task_name, start_date, end_date):
        if task_name:
            return 'yes | airflow backfill --reset_dagruns --rerun_failed_tasks -x -i -s {} -e {} -t "{}" {}'.format(
                start_date, end_date, task_name, dag_name)
        else:
            return 'yes | airflow backfill --reset_dagruns --rerun_failed_tasks -x -s {} -e {} {}'.format(
                start_date, end_date, dag_name)