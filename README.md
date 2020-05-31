# airflow-autoscaling-ecs

Setup to run Airflow in AWS ECS (Elastic Container Service) Fargate with autoscaling enabled for all services. 
All infrastructure is created with Cloudformation and Secrets are managed by AWS Secrets Manager.

## Requirements
* Create an AWS IAM User for the infrastructure deployment, with admin permissions
* Install AWS CLI running `pip install awscli`
* Setup your IAM User credentials inside `~/.aws/config`
```
    [profile my_aws_profile]
    aws_access_key_id = <my_access_key_id> 
    aws_secret_access_key = <my_secret_access_key>
    region = us-east-1
```
* Create a virtual environment
* Setup env variables in your .zshrc or .bashrc, or in your the terminal session that you are going to use:
```
	export AWS_REGION=us-east-1;
	export AWS_PROFILE=my_aws_profile;
	export ENVIRONMENT=dev;
```

## Deploy Airflow on AWS ECS
To deploy or update your stack run the following command:
```
make cloudformation-deploy
```

To destroy your stack run the following command:
```
make cloudformation-destroy
```



*Inspired by the work done by [Nicor88](https://github.com/nicor88/aws-ecs-airflow)*