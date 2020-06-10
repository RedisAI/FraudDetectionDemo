FROM redisfab/redisgears:master-x64-bionic as gears
FROM redisai/redisai:edge as ai

ENV LD_LIBRARY_PATH /usr/lib/redis/modules

COPY --from=gears /var/opt/redislabs/ /var/opt/redislabs/

# ENV PYTHONPATH /usr/lib/redis_dockers/modules/deps/cpython/Lib
ENTRYPOINT ["redis-server"]
CMD ["--loadmodule", "/usr/lib/redis/modules/redisai.so", \
    "--loadmodule", "/var/opt/redislabs/lib/modules/redisgears.so"]

ENV DEPS "python python3-pip python3-setuptools libglib2.0-0 libsm6 libxrender1 libxext6 libgomp1"
WORKDIR /data
RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends $DEPS; \
    chmod +x /usr/lib/redis/modules/redisai.so