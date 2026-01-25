#!/bin/bash

# Build and tag container images for services

set -ex

docker compose build
docker tag lwsadmin-tor lalanza808/lwsadmin-tor:latest
docker tag lwsadmin-lws lalanza808/lwsadmin-lws:latest
docker tag lwsadmin-lwsadmin lalanza808/lwsadmin-lwsadmin:latest
docker push lalanza808/lwsadmin-tor
docker push lalanza808/lwsadmin-lws
docker push lalanza808/lwsadmin-lwsadmin