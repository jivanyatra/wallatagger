#!/usr/bin/env bash

# get rid of any podman settings to use it instead of docker
unset DOCKER_HOST

# clear out any currently running and old containers
docker compose down
docker container kill wallabag_test
docker container rm wallabag_test

# check if fixtures exist in the right places
if [ ! -d "./data" ]; then
  mkdir -p ./data/db
fi

if [ ! -f "./data/db/wallabag.sqlite" ]; then
  cp ./fixtures/testdb/wallabag.sqlite ./data/db/
  cp ./fixtures/site-credentials-secret-key.txt ./data/
  chmod -R nobody:nogroup ./data/
fi

if [ ! -d "./images" ]; then
  mkdir ./images
  chmod -R nobody:nogroup ./images
fi

# using compose instead of docker run command now, cmd here for ref
docker compose up -d
#docker run -d --name wallabag_test \
#-v ./data:/var/www/wallabag/data \
#-v ./images:/var/www/wallabag/web/assets/images \
#-p 80:80 -e "SYMFONY__ENV__DOMAIN_NAME=http://localhost" \
#wallabag/wallabag
# the above docker run can work, but you should replace the volumes with:
# --mount type=bind,source=C:\absolute\path\to\folder,target=/var/www/wallabag/data
# --mount type=bind,source=C:\absolute\path\to\folder,target=/var/www/wallabag/web/assets/images

# add in custom site parser config
docker container cp ./fixtures/wired.com.txt wallabag_test:/var/www/wallabag/vendor/j0k3r/graby-site-config/
# change perms for copied file inside the container
docker exec -it wallabag_test sh -c "chmod 644 /var/www/wallabag/vendor/j0k3r/graby-site-config/wired.com.txt"
# change ownership of copied file inside the container
docker exec -it wallabag_test sh -c "chown nobody:nobody /var/www/wallabag/vendor/j0k3r/graby-site-config/wired.com.txt"

# wait for docker container to become available
sleep 4

# run tests
# pipenv run pytest
uv run pytest
