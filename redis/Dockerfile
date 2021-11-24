FROM redislabs/redisai:latest as ai

ENV LD_LIBRARY_PATH /usr/lib/redis/modules

ENTRYPOINT ["redis-server"]
CMD ["--loadmodule", "/usr/lib/redis/modules/redisai.so", "THREADS_PER_QUEUE", "2"]

ENV DEPS "python python3-pip python3-setuptools libglib2.0-0 libsm6 libxrender1 libxext6 libgomp1"
WORKDIR /data
RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends $DEPS; \
    chmod +x /usr/lib/redis/modules/redisai.so