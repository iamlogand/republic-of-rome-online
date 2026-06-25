#!/bin/bash
set -e

DOCKER_HUB_USERNAME=$(/opt/elasticbeanstalk/bin/get-config environment -k DOCKER_HUB_USERNAME)
DOCKER_HUB_TOKEN=$(/opt/elasticbeanstalk/bin/get-config environment -k DOCKER_HUB_TOKEN)

echo "$DOCKER_HUB_TOKEN" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin
