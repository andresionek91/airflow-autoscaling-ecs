#!/usr/bin/env bash
# ORIGINAL SOURCE: https://github.com/nicor88/aws-ecs-airflow/


TRY_LOOP="20"

: "${REDIS_HOST:="redis"}"
: "${REDIS_PORT:="6379"}"

: "${POSTGRES_HOST:="postgres"}"
: "${POSTGRES_PORT:="5432"}"

wait_for_port() {
  local name="$1" host="$2" port="$3"
  local j=0
  while ! nc -z "$host" "$port" >/dev/null 2>&1 < /dev/null; do
    j=$((j+1))
    if [ $j -ge $TRY_LOOP ]; then
      echo >&2 "$(date) - $host:$port still not reachable, giving up"
      exit 1
    fi
    echo "$(date) - waiting for $name... $j/$TRY_LOOP"
    sleep 5
  done
}


wait_for_port "Postgres" "$POSTGRES_HOST" "$POSTGRES_PORT"

wait_for_port "Redis" "$REDIS_HOST" "$REDIS_PORT"

case "$1" in
  webserver)
    airflow initdb
		sleep 5
    exec airflow webserver
    ;;
  worker|scheduler)
    sleep 15
    exec airflow "$@"
    ;;
  flower)
    sleep 15
    exec airflow "$@"
    ;;
  version)
    exec airflow "$@"
    ;;
  *)
    exec "$@"
    ;;
esac
