install-requirements:
	pip install -r requirements.txt

cloudformation-validate: install-requirements
	python -c 'from deploy_cloudformation import validate_templates;  validate_templates()';

infra-deploy: cloudformation-validate
	python -c 'from deploy_cloudformation import create_or_update_stacks;  create_or_update_stacks(is_foundation=True)';

push-to-ecr:
	python -c 'from deploy_docker import update_airflow_image;  update_airflow_image()';

airflow-deploy: infra-deploy push-to-ecr
	python -c 'from scripts.deploy_cloudformation import create_or_update_stacks;  create_or_update_stacks(is_foundation=False)';
	python -c 'from deploy_cloudformation import log_outputs;  log_outputs()';

airflow-update-ecs: push-to-ecr
	python -c 'from deploy_cloudformation import restart_airflow_ecs;  restart_airflow_ecs()';

airflow-destroy:
	python -c 'from deploy_cloudformation import destroy_stacks;  destroy_stacks()';
