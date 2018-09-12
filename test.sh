#!/bin/sh

docker_id="$(docker ps | awk '/flask-api-exercise_app/ {print $1}')"
docker exec -it "${docker_id}" /usr/src/app/tests/test.sh
