#!/bin/sh

CMD="$1"
TAG="$2"
REPO="airflow-${ENVIRONMENT}"

connect_to_ecr () {
    echo "Connecting to ECR"
    aws ecr get-login-password --region us-west-2 | \
    docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com"
}

validate_tag () {
    if [[ -z "${TAG}" || "${TAG}" == ""  ]] 
    then
        echo "No tag name specified for command '${CMD}'"
        echo "${CMD} usage: ./deploy_docker.sh ${CMD} <tag_name>"
        exit 1
    else
        echo "Detected image tag of: ${TAG}"
    fi
}

case ${CMD} in
    build)
        validate_tag
        connect_to_ecr
        echo "Building docker image ${REPO}:${TAG}"
        exec docker build -t ${REPO}:${TAG} .
        ;;
    tag)
        validate_tag
        echo "Tagging ecr repo: ${REPO} with tag: ${TAG}"
        exec docker tag "${REPO}:${TAG}" "${ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/${REPO}:${TAG}"
        ;;
    push)
        validate_tag
        echo "Pushing ecr repo: ${REPO} with tag: ${TAG}"
        exec docker push "${ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/${REPO}:${TAG}"
        ;;
    pull)
        validate_tag
        connect_to_ecr
        exec docker pull "${ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/${REPO}:${TAG}"
        ;;
    *)
        echo "No valid command option used"
        echo "Options: [build, tag, push, pull]"
        exec "$@"
        ;;
esac
