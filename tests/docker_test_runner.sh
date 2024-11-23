#!/usr/bin/env bash

docker compose down
docker container kill wallabag_test
docker container rm wallabag_test

if [ ! -d "./data" ]; then
  mkdir -p ./data/db
fi

if [ ! -f "./data/db/wallabag.sqlite" ]; then
  cp ./fixtures/testdb/wallabag.sqlite ./data/db/
  cp ./fixtures/site-credentials-secret-key.txt ./data/
fi

if [ ! -d "./images" ]; then
  mkdir ./images
fi

docker compose up -d
#docker run -d --name wallabag_test \
#-v ./data:/var/www/wallabag/data \
#-v ./images:/var/www/wallabag/web/assets/images \
#-p 80:80 -e "SYMFONY__ENV__DOMAIN_NAME=http://localhost" \
#wallabag/wallabag
# the above docker run can work, but you should replace the volumes with:
# --mount type=bind,source=C:\absolute\path\to\folder,target=/var/www/wallabag/data
# --mount type=bind,source=C:\absolute\path\to\folder,target=/var/www/wallabag/web/assets/images

docker container cp ./fixtures/template.com.txt wallabag_test:/var/www/wallabag/vendor/j0k3r/graby-site-config/
docker exec -it wallabag_test sh -c "chmod 644 /var/www/wallabag/vendor/j0k3r/graby-site-config/template.com.txt"
docker exec -it wallabag_test sh -c "chown nobody:nobody /var/www/wallabag/vendor/j0k3r/graby-site-config/template.com.txt"

# pipenv run pytest
