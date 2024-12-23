#!/bin/bash

POEM="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

docker-compose -f "${POEM}/docker-compose.yml" down
docker-compose -f "${POEM}/docker-compose.yml" build
docker-compose -f "${POEM}/docker-compose.yml" up