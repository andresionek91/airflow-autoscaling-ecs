install-requirements:
	pip install -r requirements.txt

cloudformation-validate: install-requirements
	python -c 'from deploy_cloudformation import validate_templates;  validate_templates()';

cloudformation-deploy: cloudformation-validate
	python -c 'from deploy_cloudformation import create_or_update_stacks;  create_or_update_stacks()';

cloudformation-destroy:
	python -c 'from deploy_cloudformation import destroy_stacks;  destroy_stacks()';

