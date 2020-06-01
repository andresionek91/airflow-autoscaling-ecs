#!/usr/bin/env bash
AWS_ACCOUNT=$(python -c 'from utils import get_aws_account_id;  get_aws_account_id()' 2>&1);
COMMIT_HASH=$(python -c 'from utils import generate_hash;  generate_hash(16)' 2>&1);
eval $(aws ecr get-login --no-include-email);

echo "Pushing image to ECR: airflow-$ENVIRONMENT:$COMMIT_HASH";
docker tag airflow-$ENVIRONMENT $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/airflow-$ENVIRONMENT:$COMMIT_HASH;
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/airflow-$ENVIRONMENT:$COMMIT_HASH;

echo "Pushing image to ECR: airflow-$ENVIRONMENT:latest";
docker tag airflow-$ENVIRONMENT $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/airflow-$ENVIRONMENT:latest;
docker push $AWS_ACCOUNT.dkr.ecr.$AWS_REGION.amazonaws.com/airflow-$ENVIRONMENT:latest;