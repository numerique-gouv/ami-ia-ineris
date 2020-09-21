#!/bin/bash

export PROJECT_CONFIG="$(cat /heka/conf/project_config.yml)"

exec entrypoint
