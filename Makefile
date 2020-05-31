install-requirements:
	pip install -r requirements.txt

cloudformation-validate: install-requirements
	python -c 'from deploy_cloudformation import validate_templates;  validate_templates()';

infra-deploy: cloudformation-validate
	python -c 'from deploy_cloudformation import create_or_update_stacks;  create_or_update_stacks(is_foundation=True)';

airflow-build:
	echo "BUILDING IMAGE: airflow-$(ENVIRONMENT):latest";
	docker build --rm -t airflow-$(ENVIRONMENT):latest .;

push-to-ecr: airflow-build
	bash push-to-ecr.sh;

airflow-deploy: infra-deploy push-to-ecr
	python -c 'from deploy_cloudformation import create_or_update_stacks;  create_or_update_stacks(is_foundation=False)';
	python -c 'from deploy_cloudformation import log_outputs;  log_outputs()';

airflow-destroy:
	python -c 'from deploy_cloudformation import destroy_stacks;  destroy_stacks()';

