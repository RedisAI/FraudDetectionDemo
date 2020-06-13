[![license](https://img.shields.io/github/license/RedisAI/FraudDetectionDemo.svg)](https://github.com/RedisAI/FraudDetectionDemo)
[![Action](https://github.com/RedisAI/FraudDetectionDemo/workflows/Docker-CI/badge.svg)](https://github.com/RedisAI/FraudDetectionDemo/actions?query=workflow%3ADocker-CI)
[![Forum](https://img.shields.io/badge/Forum-RedisAI-blue)](https://forum.redislabs.com/c/modules/redisai)
[![Gitter](https://badges.gitter.im/RedisLabs/RedisAI.svg)](https://gitter.im/RedisLabs/RedisAI?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

# FraudDetectionDemo

This demo combines several [Redis](https://redis.io) data structures and [Redis Modules](https://redis.io/topics/modules-intro)
to showcase the advantage of data locality during transaction scoring .

It uses:

* [RedisGears](https://oss.redislabs.com/redisgears/) to orchestrate the transactions and preprocessing the data
* [RedisAI](https://oss.redislabs.com/redisai/) to preproces the data and run several AI models

## Architecture
### Flow 1: Updating reference data
![Architecture](/flow1.png)
### Flow 2: Transaction scoring
![Architecture](/flow2.png)


## Running the Demo
To run the demo:
```
$ git clone https://github.com/RedisAI/FraudDetectionDemo.git
$ cd FraudDetectionDemo
# If you don't have it already, install https://git-lfs.github.com/ (On OSX: brew install git-lfs)
$ git lfs install && git lfs fetch && git lfs checkout
$ docker-compose up
```
If something went wrong, e.g. you skipped installing git-lfs, you need to force docker-compose to rebuild the containers
```
$ docker-compose up --force-recreate --build
```
Explore all data and RedisGears functions with RedisInsight
https://localhost:8001

### Testing Flow 1


### Testing Flow 2
Open a second terminal to emulate the client connecting to redis:
```
$ pip install -r example_client/requirements.txt
$ python example_client/client.py
```
