# BUILD: docker build --rm -t airflow .
# ORIGINAL SOURCE: https://github.com/puckel/docker-airflow

FROM python:3.7-slim
LABEL version="1.0"
LABEL maintainer="andresionek91"

# Never prompts the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux

# Airflow
ARG AIRFLOW_VERSION=1.10.11
ENV AIRFLOW_HOME=/usr/local/airflow
ENV AIRFLOW_GPL_UNIDECODE=yes

# celery config
ARG CELERY_REDIS_VERSION=4.2.0
ARG PYTHON_REDIS_VERSION=3.2.0

ARG TORNADO_VERSION=5.1.1
ARG WERKZEUG_VERSION=0.16.0

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8
ENV LC_ALL en_US.UTF-8

RUN set -ex \
    && buildDeps=' \
        python3-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        build-essential \
        libblas-dev \
        liblapack-dev \
        libpq-dev \
        git \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        ${buildDeps} \
        sudo \
        python3-pip \
        python3-requests \
        default-mysql-client \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat \
        locales \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow \
    && pip install -U pip setuptools wheel \
    && pip install Cython \
    && pip install pytz \
    && pip install pyOpenSSL \
    && pip install ndg-httpsclient \
    && pip install pyasn1 \
    && pip install apache-airflow[async,crypto,celery,kubernetes,jdbc,password,postgres,s3,slack,amazon]==${AIRFLOW_VERSION} \
    && pip install werkzeug==${WERKZEUG_VERSION} \
    && pip install redis==${PYTHON_REDIS_VERSION} \
    && pip install celery[redis]==${CELERY_REDIS_VERSION} \
    && pip install flask_oauthlib \
    && pip install psycopg2-binary \
    && pip install tornado==${TORNADO_VERSION} \
    && apt-get purge --auto-remove -yqq ${buildDeps} \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

COPY config/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN chown -R airflow: ${AIRFLOW_HOME}

USER airflow

COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

COPY dags ${AIRFLOW_HOME}/dags
COPY plugins ${AIRFLOW_HOME}/plugins

ENV PYTHONPATH ${AIRFLOW_HOME}

EXPOSE 8080 5555 8793

WORKDIR ${AIRFLOW_HOME}
ENTRYPOINT ["/entrypoint.sh"]
