#!/bin/bash

export PROJECT_CONFIG=$(cat /opt/app/conf/project_config.yml)
export SHARED_PROJECT_CONFIG=$(cat /opt/app/conf/shared_project_config.yml)

export PROTOCOL=$(echo "$PROJECT_CONFIG" | yq -c -r ".project.protocol")
export HOSTNAME=$(echo "$PROJECT_CONFIG" | yq -c -r ".project.hostname")
export PROJECT_NAME=$(echo "$PROJECT_CONFIG" | yq -c -r ".project.name")

envsubst '$PROTOCOL $HOSTNAME $PROJECT_NAME' < /opt/app/conf/nginx_template.conf > /etc/nginx/nginx.conf

exec nginx -g "daemon off;"
