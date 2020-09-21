#!/bin/bash

export PROJECT_CONFIG="$(cat /heka/conf/project_config.yml)"
export SHARED_PROJECT_CONFIG="$(cat /heka/conf/shared_project_config.yml)"
export PROVIDER_CREDENTIALS="$(cat /heka/conf/provider_credentials.json)"

exec python /heka/scheduler/wsgi.py
