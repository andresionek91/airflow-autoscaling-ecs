airflow-up:
	@docker-compose up --build

airflow-down:
	@docker-compose down

infra-get:
	cd infrastructure && terraform get;

infra-init: infra-get
	cd infrastructure && terraform init -upgrade;

infra-plan: infra-init
	cd infrastructure && terraform plan;

infra-apply: infra-plan
	cd infrastructure && terraform apply;

infra-destroy:
	cd infrastructure && terraform destroy;

clean:
	rm -rf postgres_data
