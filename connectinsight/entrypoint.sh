#!/bin/bash

echo "Waiting RedisInsight to start"
bash ./wait-for.sh -t 20 $APP_URL -- echo "RedisInsight is up"
echo "Excuting..."
exec "$@"
echo "done"
