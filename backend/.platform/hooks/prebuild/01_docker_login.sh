#!/bin/bash
set -e

DOCKER_HUB_USERNAME=$(aws ssm get-parameter --region eu-west-2 --name /roronline/DOCKER_HUB_USERNAME --query Parameter.Value --output text)
DOCKER_HUB_TOKEN=$(aws ssm get-parameter --region eu-west-2 --name /roronline/DOCKER_HUB_TOKEN --with-decryption --query Parameter.Value --output text)

echo "$DOCKER_HUB_TOKEN" | docker login --username "$DOCKER_HUB_USERNAME" --password-stdin
