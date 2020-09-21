#!/bin/bash

export PROJECT_CONFIG="$(cat /heka/conf/project_config.yml)"
export SHARED_PROJECT_CONFIG="$(cat /heka/conf/shared_project_config.yml)"
export PROVIDER_CREDENTIALS="$(cat /heka/conf/provider_credentials.json)"

echo "$PROVIDER_CREDENTIALS" > /etc/provider_credentials.json

gcloud auth activate-service-account --key-file=/etc/provider_credentials.json

mkdir -p /heka/storage

gsutil \
    -m  \
    -o 'GSUtil:parallel_thread_count=2' \
    -o 'GSUtil:parallel_process_count:2' \
    rsync -d -r \
    gs://heka-$(echo "$PROVIDER_CREDENTIALS" | jq -rc '.project_id' | sed 's/heka-asterix-//')-ineris-storage \
    /heka/storage

rm /etc/provider_credentials.json

exec python3 /heka/frontend/app.py
