#!/bin/bash
docker run -d -p 8083:8083 -p 8086:8086 --expose 8090 --expose 8099 -e PRE_CREATE_DB=cadvisor --name influxsrv tutum/influxdb

docker run \
--volume=/:/rootfs:ro \
--volume=/var/run:/var/run:rw \
--volume=/sys:/sys:ro \
--volume=/var/lib/docker/:/var/lib/docker:ro \
--publish=8080:8080 \
--link=influxsrv:influxsrv  \
--detach=true \
--name=cadvisor \
google/cadvisor\
-storage_driver=influxdb \
-storage_driver_db=cadvisor \
-storage_driver_host=influxsrv:8086 